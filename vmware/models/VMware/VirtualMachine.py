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
        cSpecInfo = dict()
        out = dict()

        # Put user input, data[*], into proper Input.* properties - this will simplify the rest of the code.
        for v in ("datacenterMoId", "clusterMoId", "hostMoId", "vmFolderMoId", "diskDevices", "networkDevices", "guestSpec", "vmName"):
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
            # Check target cluster/host validity.
            if Input.clusterMoId and Input.hostMoId:
                # Deploy within a preferred host in a cluster.
                self.__checkClusterValidity(Input.datacenterMoId, Input.clusterMoId)
                self.__checkHostValidity(Input.clusterMoId, Input.hostMoId)
                computeResource = host = HostSystem(self.assetId, Input.hostMoId)

            elif Input.clusterMoId and not Input.hostMoId:
                # Deploy in a cluster.
                self.__checkClusterValidity(Input.datacenterMoId, Input.clusterMoId)
                computeResource = cluster = Cluster(self.assetId, Input.clusterMoId)

            elif not Input.clusterMoId and Input.hostMoId:
                # Deploy within a standalone host (not clusterized).
                self.__checkStandaloneHostValidity(Input.datacenterMoId, Input.hostMoId)
                computeResource = host = HostSystem(self.assetId, Input.hostMoId)

            else:
                raise CustomException(status=400, payload={"VMware": "missing cluster and/or host parameters."})

            # Check target datastore/network validity for computeResource (cluster or single host).
            for ds in Input.datastoreMoId:
                self.__checkDatastoreValidity(computeResource, ds)

            for net in Input.networkMoId:
                self.__checkNetworkValidity(computeResource, net)








            # Build devsSpecs.
            if Input.diskDevices:
                devsSpecs = self.buildStorageSpec(Input.diskDevices, Input.datastoreMoId)

            if Input.networkDevices:
                nicsSpecs = self.buildNetworkSpec(Input.networkDevices)
                if devsSpecs:
                    devsSpecs.extend(nicsSpecs)
                else:
                    devsSpecs = nicsSpecs

            datastore = Datastore(self.assetId, Input.datastoreMoId[0]) # todo: [0] is added for compatibility but code needs to do a for cycle ?.
            vmFolder = VirtualMachineFolder(self.assetId, Input.vmFolderMoId)

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

    def __checkClusterValidity(self, datacenterMoId: str, clusterMoId: str) -> None:
        from vmware.models.VMware.Datacenter import Datacenter

        if clusterMoId:
            try:
                datacenter = Datacenter(self.assetId, datacenterMoId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

            try:
                if clusterMoId not in datacenter:
                    raise CustomException(status=400, payload={"VMware": "cluster not found in this datacenter."})
            except Exception as e:
                raise e



    def __checkHostValidity(self, clusterMoId: str, hostMoId: str) -> None:
        from vmware.models.VMware.Cluster import Cluster

        if hostMoId:
            try:
                cluster = Cluster(self.assetId, clusterMoId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "invalid cluster."})

            try:
                if hostMoId not in cluster:
                    raise CustomException(status=400, payload={"VMware": "host not found in this cluster."})
            except Exception as e:
                raise e



    def __checkStandaloneHostValidity(self, datacenterMoId: str, hostMoId: str) -> None:
        from vmware.models.VMware.Datacenter import Datacenter

        if hostMoId:
            try:
                datacenter = Datacenter(self.assetId, datacenterMoId)
            except Exception:
                raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

            try:
                if hostMoId not in datacenter:
                    raise CustomException(status=400, payload={"VMware": "host not found in this datacenter."})
            except Exception as e:
                raise e



    def __checkDatastoreValidity(self, computeResource: object, datastoreMoId: str) -> None:
        if datastoreMoId:
            try:
                if datastoreMoId not in computeResource:
                    raise CustomException(status=400, payload={"VMware": "datastore not found in this cluster."})
            except Exception as e:
                raise e



    def __checkNetworkValidity(self, computeResource: object, networkMoId: str) -> None:
        if networkMoId:
            try:
                if networkMoId not in computeResource:
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
