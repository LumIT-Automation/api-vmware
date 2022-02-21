from typing import List
from pyVmomi import vim

from vmware.models.VMware.VmNetworkAdapter import VmNetworkAdapter
from vmware.models.VMware.VirtualMachineDatastore import VirtualMachineDatastore
from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

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

        self.networkDevices: List[VmNetworkAdapter] = []
        self.diskDevices: List[VirtualMachineDatastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def deploy(self, data: dict) -> dict:
        from vmware.models.VMware.Cluster import Cluster
        from vmware.models.VMware.Datastore import Datastore
        from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
        from vmware.models.VMware.CustomSpec import CustomSpec
        try:
            # Perform some preliminary checks.
            if self.__isClusterValid(data["datacenterId"], data["clusterId"]):
                if self.__isDatastoreValid(data["clusterId"], data["datastoreId"]):
                    if "networkId" not in data or self.__isNetworkValid(data["clusterId"], data["networkId"]): # Allow to deploy a VM without touch the network card.
                        devsSpecs = None
                        cloneSpec = vim.vm.CloneSpec() # virtual machine specifications.

                        cluster = Cluster(self.assetId, data["clusterId"])
                        datastore = Datastore(self.assetId, data["datastoreId"])
                        vmFolder = VirtualMachineFolder(self.assetId, data["vmFolderId"])

                        # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
                        relocateSpec = vim.vm.RelocateSpec()
                        relocateSpec.datastore = datastore.oDatastore
                        relocateSpec.pool = cluster.oCluster.resourcePool # The resource pool associated to this cluster.

                        cloneSpec.location = relocateSpec
                        cloneSpec.powerOn = data["powerOn"]
                        cloneSpec.config = vim.vm.ConfigSpec()

                        if "diskDevices" in data:
                            devsSpecs = self.buildStorageSpec(data["diskDevices"])
                        if "networkDevices" in data:
                            nicsSpec = self.buildNetworkSpec(data["networkDevices"])
                            if devsSpecs:
                                devsSpecs.extend(nicsSpec)
                            else:
                                devsSpecs = nicsSpec
                        if devsSpecs:
                            cloneSpec.config.deviceChange = devsSpecs

                        # Apply the guest OS customization specifications.
                        if "guestSpec" in data and data["guestSpec"]:
                            cs = CustomSpec(self.assetId, data["guestSpec"]).raw()
                            cloneSpec.customization = cs.spec

                        # Deploy
                        task = self.oVirtualMachine.Clone(folder=vmFolder.oVMFolder, name=data["vmName"], spec=cloneSpec)
                        taskId = task._GetMoId()
                        return dict({
                            "task": taskId
                        })

        except Exception as e:
            raise e



    def clone(self, data: dict) -> dict: # alias.
        return self.deploy(data)



    def modify(self, data: dict) -> dict:
        disksSpec = None
        nicsSpec = None
        devsSpecs = None
        modifySpec = vim.vm.ConfigSpec()
        try:
            if "numCpu" in data and data["numCpu"]:
                modifySpec.numCPUs = data["numCpu"]
            if "numCoresPerSocket" in data and data["numCoresPerSocket"]:
                modifySpec.numCoresPerSocket = data["numCoresPerSocket"]
            if "memoryMB" in data and data["memoryMB"]:
                modifySpec.memoryMB = data["memoryMB"]
            if "notes" in data and data["notes"]:
                modifySpec.annotation = data["notes"]

            if "diskDevices" in data:
                devsSpecs = self.buildStorageSpec(data["diskDevices"])
            if "networkDevices" in data:
                nicsSpec = self.buildNetworkSpec(data["networkDevices"])
                if devsSpecs:
                    devsSpecs.extend(nicsSpec)
                else:
                    devsSpecs = nicsSpec
            if devsSpecs:
                modifySpec.deviceChange = devsSpecs

            task = self.oVirtualMachine.ReconfigVM_Task(spec=modifySpec)
            taskId = task._GetMoId()
            return dict({
                "task": taskId
            })

        except Exception as e:
            raise e



    def loadVMDatastores(self) -> None:
        try:
            for l in self.listVMDiskInfo():
                self.diskDevices.append(
                    VirtualMachineDatastore(self.assetId, l["datastore"], l["label"], l["size"], l["deviceType"])
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

        try:
            config = self.oVirtualMachine.config

            if related:
                # Get virtual disks info.
                self.loadVMDatastores()
                for disk in self.diskDevices:
                    vmDisks.append(
                        disk.info()
                    )

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
            datacenter.loadClusters()
            for cluster in datacenter.clusters:
                if clusterMoId == cluster.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "cluster not found in this datacenter."})
        except Exception as e:
            raise e



    def __isDatastoreValid(self, clusterMoId: str, datastoreMoId: str) -> bool:
        from vmware.models.VMware.Cluster import Cluster

        try:
            cluster = Cluster(self.assetId, clusterMoId)
            cluster.loadDatastores()
            for datastore in cluster.datastores:
                if datastoreMoId == datastore.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "datastore not found in this cluster."})
        except Exception as e:
            raise e



    def __isNetworkValid(self, clusterMoId: str, networkMoId: str) -> bool:
        from vmware.models.VMware.Cluster import Cluster

        try:
            cluster = Cluster(self.assetId, clusterMoId)
            cluster.loadNetworks()
            for network in cluster.networks:
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



    ####################################################################################################################
    # Protected static methods
    ####################################################################################################################

    @staticmethod
    def _cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "list":
                if not o["networkDevices"]:
                    del (o["networkDevices"])
                if not o["diskDevices"]:
                    del (o["diskDevices"])
        except Exception:
            pass

        return o
