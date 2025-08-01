import re
from typing import List

from django.conf import settings

from vmware.models.VMware.VmNetworkAdapter import VmNetworkAdapter
from vmware.models.VMware.VirtualMachineDatastore import VirtualMachineDatastore
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.CustomSpec import CustomSpec
from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend
from vmware.models.VMware.backend.VirtualMachineSpecsBuilder import VirtualMachineSpecsBuilder as SpecsBuilder

from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Stage2.TargetCommand import TargetCommand
from vmware.models.Stage2.Command import Command
from vmware.tasks import pollVmwareAsync_task

from vmware.helpers.VMware.VmwareHelper import VmwareHelper
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class InputData:
    def __init__(self, *args, **kwargs):
        self.datacenterMoId = None
        self.clusterMoId = None
        self.hostMoId = None
        self.mainDatastoreMoId = None
        self.datastoreMoId = []
        self.networkMoId = []
        self.vmFolderMoId = None
        self.diskDevices = None
        self.networkDevices = None
        self.guestSpec = None
        self.deleteGuestSpecAfterDeploy = False
        self.vmName = None
        self.bootstrapKeyId = None
        self.secondStageIp = None
        self.postDeployCommands: List[dict] = None



class VirtualMachine(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVirtualMachine.name
        self.guestName: str
        self.version: str
        self.uuid: str
        self.numCpu: int
        self.numCoresPerSocket: int
        self.memoryMB: int
        self.template: bool
        self.notes: str = ""

        self.networkDevices: List[VmNetworkAdapter] = []
        self.diskDevices: List[VirtualMachineDatastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def deploy(self, data: dict) -> dict:
        from vmware.models.VMware.Cluster import Cluster
        from vmware.models.VMware.HostSystem import HostSystem
        from vmware.models.VMware.Datastore import Datastore
        from vmware.models.VMware.FolderVM import FolderVM
        from vmware.models.VMware.CustomSpec import CustomSpec

        oCustomSpec = None
        host = None
        cluster = None
        cSpecInfo = dict()
        out = dict()
        Input = InputData()

        # Put user input, data[*], into proper Input.* properties - this will simplify the rest of the code.
        Input.networkMoId = [] # safe to controller locks.
        Input.datastoreMoId = []
        for v in ("datacenterMoId", "clusterMoId", "hostMoId", "mainDatastoreMoId", "vmFolderMoId", "diskDevices",
                  "networkDevices", "guestSpec", "deleteGuestSpecAfterDeploy", "secondStageIp", "vmName", "bootstrapKeyId", "postDeployCommands"):
            setattr(Input, v, data.get(v, None))
        for v in ("networkDevices", "diskDevices"):
            for e in ("existent", "new"):
                try:
                    for n in data[v][e]:
                        if v == "networkDevices":
                            Input.networkMoId.append(n["networkMoId"])
                        else:
                            Input.datastoreMoId.append(n["datastoreMoId"])
                except Exception:
                    pass

        try:
            # Define if target is cluster or host and check its validity.
            if Input.clusterMoId and Input.hostMoId:
                # Deploy within a preferred host in a cluster.
                self.__checkCluster(Input.datacenterMoId, Input.clusterMoId)
                self.__checkHost(Input.clusterMoId, Input.hostMoId)
                cluster = Cluster(self.assetId, Input.clusterMoId)
                computeResource = host = HostSystem(self.assetId, Input.hostMoId)

            elif Input.clusterMoId and not Input.hostMoId:
                # Deploy in a cluster.
                self.__checkCluster(Input.datacenterMoId, Input.clusterMoId)
                computeResource = cluster = Cluster(self.assetId, Input.clusterMoId)

            elif not Input.clusterMoId and Input.hostMoId:
                # Deploy within a standalone host (not clusterized).
                self.__checkStandaloneHost(Input.datacenterMoId, Input.hostMoId)
                computeResource = host = HostSystem(self.assetId, Input.hostMoId)

            else:
                raise CustomException(status=400, payload={"VMware": "Missing cluster and/or host parameters."})

            # Check target datastore/network validity for computeResource (cluster or single host).
            for ds in (Input.datastoreMoId + [Input.mainDatastoreMoId]):
                self.__checkDatastore(computeResource, ds)

            for net in Input.networkMoId:
                self.__checkNetwork(computeResource, net)

            # Check bootstrapKey.
            self.__checkBootstrapKey(Input.bootstrapKeyId)

            # Check post deploy commands.
            self.__checkPostDeployCommands(Input.postDeployCommands)

            # Build devsSpecs.
            specsBuilder = SpecsBuilder(self.assetId, self.moId)

            if Input.diskDevices:
                specsBuilder.buildStorageSpec(Input.diskDevices, Input.datastoreMoId)
            if Input.networkDevices:
                specsBuilder.buildNetworkSpec(Input.networkDevices)

            devSpecs = specsBuilder.storageSpec + specsBuilder.networkSpec

            # Apply the guest OS customization specifications.
            if Input.guestSpec:
                oCustomSpec = CustomSpec(self.assetId).oCustomSpec(Input.guestSpec)
                cSpecInfo = CustomSpec(self.assetId, Input.guestSpec).info()

            # If settings.NEW_VM_CHECK_IP_IN_PG is true (default), check if the ip addresses of the new VM are already used.
            if settings.NEW_VM_CHECK_IP_IN_PG and "network" in cSpecInfo:
                self.__checkNewVMIpAddress(networkSpecInfo=cSpecInfo["network"], networkMoIdList=Input.networkMoId)

            # Put all together: build the cloneSpec.
            specsBuilder.buildVMCloneSpecs(
                oDatastore=Datastore(self.assetId, Input.mainDatastoreMoId).oDatastore,
                devsSpecs=devSpecs,
                cluster=cluster,
                host=host,
                data=data,
                oCustomSpec=oCustomSpec
            )

            Log.log("Virtual Machine clone operation specs: "+str(specsBuilder.cloneSpec))

            # Deploy.
            out["task_moId"] = self.clone(
                oVMFolder=FolderVM(self.assetId, Input.vmFolderMoId).oVMFolder,
                vmName=Input.vmName,
                cloneSpec=specsBuilder.cloneSpec
            )

            # A worker will poll the vCenter and update the target table on stage2 database in order to track progress.
            out["targetId"] = self.pollVmwareDeployVMTask(
                bootStrapKeyId=Input.bootstrapKeyId,
                userName="root",
                taskMoId=out["task_moId"],
                vmName=Input.vmName,
                customSpecInfo=cSpecInfo,
                postDeployCommands=Input.postDeployCommands,
                guestSpec=Input.guestSpec,
                secondStageIp=Input.secondStageIp
            )

            return out
        except Exception as e:
            raise e
        finally:
            if Input.deleteGuestSpecAfterDeploy:
                VirtualMachine.__deleteGuestSpec(assetId=self.assetId, guestSpec=Input.guestSpec)



    def pollVmwareDeployVMTask(self, bootStrapKeyId: int, userName: str, taskMoId: str, vmName: str, customSpecInfo: dict, postDeployCommands: list = None, guestSpec: str = "", secondStageIp: str = "") -> int:
        postDeployCommands = [] if postDeployCommands is None else postDeployCommands
        ip = ""

        try:
            # Set up the IPv4 address which the second stage worker will SSH into.
            if secondStageIp:
                ip = secondStageIp
            elif "network" in customSpecInfo and customSpecInfo["network"][0] and "ip" in customSpecInfo["network"][0]:
                ip = customSpecInfo["network"][0]["ip"]

            if customSpecInfo["type"] == "Linux" and bool(ip):
                disableSecondStage = False
            else:
                disableSecondStage = True

            targetData = {
                "ip": ip,
                "port": 22,
                "api_type": "ssh",
                "id_bootstrap_key": bootStrapKeyId,
                "username": userName,
                "id_asset": self.assetId,
                "task_moId": taskMoId,
                "vm_name": vmName
            }

            # Add target do db.
            targetId = Target.add(targetData)

            # Insert in the db the sequence of the commands to be executed on the target.
            for c in postDeployCommands:
                c["id_target"] = targetId
                TargetCommand.add(c)

            # Launch async worker.
            # Disable second stage if no IPv4 is assigned.
            pollVmwareAsync_task.delay(assetId=self.assetId, taskMoId=taskMoId, targetId=targetId, guestSpec=guestSpec, forceDisableSecondStage=disableSecondStage)

            return targetId
        except Exception as e:
            raise e



    def modify(self, data: dict) -> str:
        try:
            specsBuilder = SpecsBuilder(self.assetId, self.moId)
            vmDatastoreMoId = self.info(related=False)["defaultDatastoreMoId"]

            if "diskDevices" in data:
                specsBuilder.buildStorageSpec(data["diskDevices"], vmDatastoreMoId)
                data.pop("diskDevices")
            if "networkDevices" in data:
                specsBuilder.buildNetworkSpec(data["networkDevices"])
                data.pop("networkDevices")

            devSpecs = specsBuilder.storageSpec + specsBuilder.networkSpec
            specsBuilder.buildVMConfigSpecs(data, devSpecs)
            modifySpec = specsBuilder.configSpec

            return self.reconfig(configSpec=modifySpec)
        except Exception as e:
            raise e



    def customizeGuestOS(self, data: dict) -> str:
        try:
            if "specName" in data and data["specName"]:
                customSpec = CustomSpec(self.assetId, data["specName"])
                return customSpec.customizeGuestOS(self.oVirtualMachine) # Task
        except Exception as e:
            raise e



    def loadVMDatastores(self) -> None:
        try:
            for l in self.getDisksInformation():
                self.diskDevices.append(
                    VirtualMachineDatastore(self.assetId, l["datastore"], l["label"], l["sizeMB"], l["deviceType"])
                )
        except Exception as e:
            raise e



    def loadVMNetworks(self) -> None:
        try:
            for l in self.getNetworkInformation():
                self.networkDevices.append(
                    VmNetworkAdapter(self.assetId, l["network"], l["label"], l["deviceType"])
                )
        except Exception as e:
            raise e



    def guestInfo(self) -> dict:
        try:
            return Backend.guestInfo(self)
        except Exception as e:
            raise e



    # Set all the nics of the virtual machine as connected/disconnected to the associate port group.
    def nicConnection(self, connected: bool):
        devChange = list()

        try:
            specsBuilder = SpecsBuilder(self.assetId, self.moId)
            modifySpec = specsBuilder.configSpec

            for nic in self.oNicList():
                devChange.append(self.nicConnectSpec(oNic=nic, connected=connected))
            modifySpec.deviceChange = devChange

            Log.log("Reconfiguring virtual Machine nics as: \"connected\": " + str(connected))
            Log.log("Reconfigure operation specs: " + str(devChange))
            self.reconfig(configSpec=modifySpec)
        except Exception as e:
            raise e



    def info(self, related: bool = True) -> dict:
        vmDisks = list()
        vmNets = list()
        defaultDatastoreMoId = ""

        try:
            config = self.oVirtualMachine.config
            if related:
                # Get virtual disks info.
                self.loadVMDatastores()
                for disk in self.diskDevices:
                    vmDisks.append(
                        disk.info()
                    )

                # Get the datastore where the vmx file is contained.
                defaultDatastoreName = re.findall('\[(.*)\]', config.files.vmPathName)[0]
                defaultDatastoreMoId = Datastore.getDatastoreMoIdByName(self.assetId, defaultDatastoreName)

                # Get network devices info.
                self.loadVMNetworks()
                for net in self.networkDevices:
                    vmNets.append(
                        net.info()
                    )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": config.name,
                "defaultDatastoreMoId": defaultDatastoreMoId,
                "guestName": config.guestFullName,
                "version": config.version,
                "uuid": config.uuid,
                "numCpu": config.hardware.numCPU,
                "numCoresPerSocket": config.hardware.numCoresPerSocket,
                "memoryMB": config.hardware.memoryMB,
                "template": config.template,
                "notes": config.annotation,

                "networkDevices": {
                    "existent": vmNets
                },
                "diskDevices": {
                    "existent": vmDisks
                }
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __checkCluster(self, datacenterMoId: str, clusterMoId: str) -> None:
        from vmware.models.VMware.Datacenter import Datacenter

        if clusterMoId:
            try:
                datacenter = Datacenter(self.assetId, datacenterMoId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "Invalid datacenter."})

            try:
                if clusterMoId not in datacenter:
                    raise CustomException(status=400, payload={"VMware": "Cluster not found in this datacenter."})
            except Exception as e:
                raise e



    def __checkHost(self, clusterMoId: str, hostMoId: str) -> None:
        from vmware.models.VMware.Cluster import Cluster

        if hostMoId:
            try:
                cluster = Cluster(self.assetId, clusterMoId)
                if hostMoId not in cluster:
                    raise CustomException(status=400, payload={"VMware": "Host not found in this cluster."})
            except Exception as e:
                raise e



    def __checkStandaloneHost(self, datacenterMoId: str, hostMoId: str) -> None:
        from vmware.models.VMware.Datacenter import Datacenter

        if hostMoId:
            try:
                datacenter = Datacenter(self.assetId, datacenterMoId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "Invalid datacenter."})

            try:
                if hostMoId not in datacenter:
                    raise CustomException(status=400, payload={"VMware": "Host not found in this datacenter."})
            except Exception as e:
                raise e



    def __checkDatastore(self, computeResource: object, datastoreMoId: str) -> None:
        if datastoreMoId:
            try:
                if datastoreMoId not in computeResource: # host or cluster.
                    raise CustomException(status=400, payload={"VMware": "Datastore not found in this cluster."})
            except Exception as e:
                raise e



    def __checkNetwork(self, computeResource: object, networkMoId: str) -> None:
        if networkMoId:
            try:
                if networkMoId not in computeResource: # host or cluster.
                    raise CustomException(status=400, payload={"VMware": "Network not attached to this cluster."})
            except Exception as e:
                raise e



    def __checkBootstrapKey(self, keyId: int) -> None:
        if keyId:
            try:
                BootstrapKey(keyId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "Invalid bootstrap key."})



    def __checkPostDeployCommands(self, commandIds: list = None) -> None:
        commandIds = [] if commandIds is None else commandIds
        for c in commandIds:
            if c:
                try:
                    Command(c["command"])
                except Exception:
                    raise CustomException(status=400, payload={"VMware": "Invalid post-deploy command identifier."})



    def __checkNewVMIpAddress(self, networkSpecInfo: object, networkMoIdList: list ) -> None:
        from vmware.models.VMware.Network import Network

        try:
            n = 0
            for net in networkSpecInfo:
                if "ip" in net and net["ip"] and networkMoIdList[n]:
                    Log.actionLog("Deploy VM: check if the ip address "+net["ip"]+" is used in network "+networkMoIdList[n])
                    networkIp = Network(assetId=self.assetId, moId=networkMoIdList[n]).findVMsWithThisIpAddress(ipAddress=net["ip"], checkNetworksWithSameVlanIds=settings.NEW_VM_CHECK_IP_IN_PGS_SAME_VLANID)
                    if networkIp:
                        raise CustomException(status=400, payload={"VMware": "The IP address "+net["ip"]+" is already in use in this vCenter. Details: "+str(networkIp)})
                    else:
                        Log.actionLog("Deploy VM: the IP "+net["ip"]+" seems unused.")
                n += 1

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        virtualmachines = list()

        try:
            for o in Backend.oVirtualMachines(assetId):
                virtualmachine = VirtualMachine(assetId, VmwareHelper.getInfo(o)["moId"])
                virtualmachines.append(
                    VirtualMachine._cleanup("list", virtualmachine.info(related))
                )

            return virtualmachines
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        virtualmachines = list()

        try:
            for o in Backend.oVirtualMachines(assetId):
                virtualmachine = VmwareHelper.getInfo(o)
                virtualmachine["assetId"] = assetId
                virtualmachines.append(virtualmachine)

            return virtualmachines
        except Exception as e:
            raise e



    @staticmethod
    def getVmObjFromName(assetId: int, vmName: str):
        try:
            for o in Backend.oVirtualMachines(assetId):
                vm = VmwareHelper.getInfo(o)
                if vm["name"] == vmName:
                    return VirtualMachine(assetId, VmwareHelper.getInfo(o)["moId"])
            return None
        except Exception as e:
            raise e



    ####################################################################################################################
    # Protected static methods
    ####################################################################################################################

    @staticmethod
    def _cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "list":
                if not o["networkDevices"] or not o["networkDevices"]["existent"]:
                    del (o["networkDevices"])

                if not o["diskDevices"] or not o["diskDevices"]["existent"]:
                    del (o["diskDevices"])

                if not o["defaultDatastoreMoId"]:
                    del (o["defaultDatastoreMoId"])
        except Exception:
            pass

        return o



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __deleteGuestSpec(assetId, guestSpec):
        if guestSpec:
            try:
                Log.actionLog("Deleting guest spec: " + str(guestSpec))
                CustomSpec(assetId, guestSpec).delete()
            except Exception:
                pass
