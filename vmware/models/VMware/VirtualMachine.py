import re
from typing import List
from dataclasses import dataclass

from vmware.models.VMware.VmNetworkAdapter import VmNetworkAdapter
from vmware.models.VMware.VirtualMachineDatastore import VirtualMachineDatastore
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.models.Stage2.Target import Target
from vmware.tasks import poolVmwareAsync_task

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


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
        from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
        from vmware.models.VMware.CustomSpec import CustomSpec

        devsSpecs = None
        oCustomSpec = None
        host = None
        cluster = None
        computeResource = None
        cSpecInfo = dict()
        out = dict()

        @dataclass
        class Input:
            datacenterMoId = None
            clusterMoId = None
            hostMoId = None
            datastoreMoId = []
            networkMoId = []
            vmFolderMoId = None
            diskDevices = None
            networkDevices = None
            guestSpec = None
            vmName = None

        for v in ("datacenterMoId", "clusterMoId", "hostMoId", "vmFolderMoId", "diskDevices", "networkDevices", "guestSpec", "vmName"):
            setattr(Input, v, data.get(v, None))

        if "networkDevices" in data:
            if "existent" in data["networkDevices"]:
                for n in data["networkDevices"]["existent"]:
                    if "networkMoId" in n:
                        Input.networkMoId.append(n["networkMoId"])

            if "new" in data["networkDevices"]:
                for n in data["networkDevices"]["new"]:
                    if "networkMoId" in n:
                        Input.networkMoId.append(n["networkMoId"])

        if "diskDevices" in data:
            if "existent" in data["diskDevices"]:
                for n in data["diskDevices"]["existent"]:
                    if "datastoreMoId" in n:
                        Input.datastoreMoId.append(n["datastoreMoId"])

            if "new" in data["diskDevices"]:
                for n in data["diskDevices"]["new"]:
                    if "datastoreMoId" in n:
                        Input.datastoreMoId.append(n["datastoreMoId"])

        try:
            if Input.clusterMoId and Input.hostMoId:
                # Deploy within a preferred host in cluster in a cluster.
                if self.__isClusterValid(Input.datacenterMoId, Input.clusterMoId):
                    cluster = Cluster(self.assetId, Input.clusterMoId)
                    if self.__isHostValid(Input.clusterMoId, Input.hostMoId):
                        host = HostSystem(self.assetId, Input.hostMoId)
                        computeResource = host

            elif Input.clusterMoId and not Input.hostMoId:
                # Deploy within a specific host of the cluster.
                if self.__isClusterValid(Input.datacenterMoId, Input.clusterMoId):
                    cluster = Cluster(self.assetId, Input.clusterMoId)
                    computeResource = cluster

            elif not Input.clusterMoId and Input.hostMoId:
                # Deploy within a standalone host (not clusterized).
                if self.__isStandaloneHostValid(Input.datacenterMoId, Input.hostMoId):
                    host = HostSystem(self.assetId, Input.hostMoId)
                    computeResource = host
            else:
                raise CustomException(status=400, payload={"VMware": "missing cluster and/or host parameters."})


            # TEMPORARY CODE ###########################################################################################
            Input.datastoreMoId = str(Input.datastoreMoId[0])
            Input.networkMoId = str(Input.networkMoId[0])
            #@todo: check against every datastore and netw.
            # END TEMPORARY CODE #######################################################################################


            # Check datastore/network connection for computeResource (cluster or single host).
            if self.__isDatastoreValid(computeResource, Input.datastoreMoId):
                if "networkId" not in data or self.__isNetworkValid(computeResource, Input.networkMoId):  # Allow to deploy a VM without touching the network card.
                    datastore = Datastore(self.assetId, Input.datastoreMoId)
                    vmFolder = VirtualMachineFolder(self.assetId, Input.vmFolderMoId)

                    if Input.diskDevices:
                        devsSpecs = self.buildStorageSpec(Input.diskDevices, Input.datastoreMoId)
                    if Input.networkDevices:
                        nicsSpecs = self.buildNetworkSpec(Input.networkDevices)
                        if devsSpecs:
                            devsSpecs.extend(nicsSpecs)
                        else:
                            devsSpecs = nicsSpecs

                        # Apply the guest OS customization specifications.
                        if Input.guestSpec:
                            oCustomSpec = CustomSpec(self.assetId).oCustomSpec(Input.guestSpec)
                            cSpecInfo = CustomSpec(self.assetId, Input.guestSpec).info()

                        # Put all together.
                        cloneSpec = self.buildVMCloneSpecs(oDatastore=datastore.oDatastore, devsSpecs=devsSpecs, cluster=cluster, host=host, data=data, oCustomSpec=oCustomSpec)

                        # Deploy
                        out["task_moId"] = self.clone(oVMFolder=vmFolder.oVMFolder, vmName=Input.vmName, cloneSpec=cloneSpec)

                        if cSpecInfo:
                            out["targetId"] = self.poolVmwareDeployVMTask(bootStrapKeyId=1, userName="root", taskMoId=out["task_moId"], customSpecInfo=cSpecInfo)

                        return out
        except Exception as e:
            raise e



    def poolVmwareDeployVMTask(self, bootStrapKeyId: int, userName: str, taskMoId: str, customSpecInfo: dict) -> int:
        try:
            if "network" in customSpecInfo and customSpecInfo["network"][0] and "ip" in customSpecInfo["network"][0]:
                targetData = {
                    "ip": customSpecInfo["network"][0]["ip"],
                    "port": 22,
                    "api_type": "ssh",
                    "id_bootstrap_key": bootStrapKeyId,
                    "username": userName,
                    "id_asset": self.assetId,
                    "task_moId": taskMoId
                }

                targetId = Target.add(targetData)
                poolVmwareAsync_task.delay(assetId=self.assetId, taskMoId=taskMoId, targetId=targetId)
                return targetId
        except Exception as e:
            raise e



    def modify(self, data: dict) -> str:
        devsSpecs = None

        try:
            vmDatastoreMoId = self.info(related=False)["defaultDatastoreMoId"]
            if "diskDevices" in data:
                devsSpecs = self.buildStorageSpec(data["diskDevices"], vmDatastoreMoId)
                data.pop("diskDevices")
            if "networkDevices" in data:
                nicsSpec = self.buildNetworkSpec(data["networkDevices"])
                data.pop("networkDevices")
                if devsSpecs:
                    devsSpecs.extend(nicsSpec)
                else:
                    devsSpecs = nicsSpec

            modifySpec = self.buildVMConfigSpecs(data, devsSpecs)

            return self.reconfig(configSpec=modifySpec)
        except Exception as e:
            raise e



    def loadVMDatastores(self) -> None:
        try:
            for l in self.listVMDiskInfo():
                self.diskDevices.append(
                    VirtualMachineDatastore(self.assetId, l["datastore"], l["label"], l["sizeMB"], l["deviceType"])
                )
        except Exception as e:
            raise e



    def loadVMNetworks(self) -> None:
        try:
            for l in self.listVMNetworkInfo():
                self.networkDevices.append(
                    VmNetworkAdapter(self.assetId, l["network"], l["label"], l["deviceType"])
                )
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

    def __isClusterValid(self, datacenterMoId: str, clusterMoId: str) -> bool:
        from vmware.models.VMware.Datacenter import Datacenter
        try:
            datacenter = Datacenter(self.assetId, datacenterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

        try:
            if clusterMoId in datacenter:
                return True
            else:
                raise CustomException(status=400, payload={"VMware": "cluster not found in this datacenter."})
        except Exception as e:
            raise e



    def __isHostValid(self, clusterMoId: str, hostMoId: str) -> bool:
        from vmware.models.VMware.Cluster import Cluster
        try:
            cluster = Cluster(self.assetId, clusterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid cluster."})

        try:
            cluster.loadHosts()
            for host in cluster.hosts:
                if hostMoId == host.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "host not found in this cluster."})
        except Exception as e:
            raise e



    def __isStandaloneHostValid(self, datacenterMoId: str, hostMoId: str) -> bool:
        from vmware.models.VMware.Datacenter import Datacenter

        try:
            datacenter = Datacenter(self.assetId, datacenterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

        try:
            datacenter.loadHosts()
            for host in datacenter.standalone_hosts:
                if hostMoId == host.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "host not found in this datacenter."})
        except Exception as e:
            raise e



    # computeResource can be a cluster or a single host.
    def __isDatastoreValid(self, computeResource: object, datastoreMoId: str) -> bool:
        try:
            computeResource.loadDatastores()
            for datastore in computeResource.datastores:
                if datastoreMoId == datastore.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "datastore not found in this cluster."})
        except Exception as e:
            raise e



    # computeResource can be a cluster or a single host.
    def __isNetworkValid(self, computeResource: object, networkMoId: str) -> bool:
        try:
            computeResource.loadNetworks()
            for network in computeResource.networks:
                if networkMoId == network.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "network not attached to this cluster."})
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
                virtualmachine = VirtualMachine(assetId, VmwareHelper.vmwareObjToDict(o)["moId"])
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
                virtualmachine = VmwareHelper.vmwareObjToDict(o)
                virtualmachine["assetId"] = assetId
                virtualmachines.append(virtualmachine)

            return virtualmachines
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
