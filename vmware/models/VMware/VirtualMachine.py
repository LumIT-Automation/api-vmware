from typing import List
from pyVmomi import vim

from vmware.models.VMware.VirtualMachineNetwork import VirtualMachineNetwork
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

        self.vmNetworks: List[VirtualMachineNetwork] = []
        self.vmDatastores: List[VirtualMachineDatastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def deploy(self, data: dict) -> dict:
        #from vmware.models.VMware.Network import Network
        #from vmware.models.VMware.Cluster import Cluster
        #from vmware.models.VMware.VMFolder import VMFolder
        try:
            # Perform some preliminary checks.
            if self.__isClusterValid(data["datacenterId"], data["clusterId"]):
                if self.__isDatastoreValid(data["clusterId"], data["datastoreId"]):
                    if self.__isNetworkValid(data["clusterId"], data["networkId"]):

                        raise Exception
                        # @todo.

                        vmFolder = VMFolder(self.assetId, data["vmFolderId"])
                        vmFolder.getVMwareObject()
                        vmFolderObj = vmFolder.oCluster

                        # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
                        relocateSpec = vim.vm.RelocateSpec()
                        relocateSpec.datastore = datastoreObj
                        relocateSpec.pool = clusterObj.resourcePool # The resource pool associated to this cluster.

                        # VirtualMachineCloneSpec(vim.vm.CloneSpec): virtual machine specifications.
                        cloneSpec = vim.vm.CloneSpec()
                        cloneSpec.location = relocateSpec
                        cloneSpec.powerOn = data["powerOn"]

                        self.getVMwareObject()
                        # Deploy
                        task = self.oVirtualMachine.Clone(folder=vmFolderObj, name=data["vmName"], spec=cloneSpec)

                        return dict({
                            "task": task._GetMoId()
                        })

        except Exception as e:
            raise e



    def clone(self, data: dict): # alias.
        self.deploy(data)



    def loadVMDatastores(self) -> None:
        try:
            for l in self.listVMDiskInfo():
                self.vmDatastores.append(
                    VirtualMachineDatastore(self.assetId, l["datastore"], l["label"], l["size"])
                )
        except Exception as e:
            raise e



    def loadVMNetworks(self) -> None:
        try:
            for l in self.listVMNetworkInfo():
                self.vmNetworks.append(
                    VirtualMachineNetwork(self.assetId, l["network"], l["label"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = False) -> dict:
        vmDisks = list()
        vmNets = list()

        try:
            config = self.oVirtualMachine.config
            if related:
                self.loadVMDatastores()
                self.loadVMNetworks()

            # Get network devices info.
            for net in self.vmNetworks:
                vmNets.append(
                    net.info()
                )

            # Get virtual disks info.
            for disk in self.vmDatastores:
                vmDisks.append(
                    disk.info()
                )

            return {
                "moId": self.moId,
                "name": config.name,
                "guestName": config.guestFullName,
                "version": config.version,
                "uuid": config.uuid,
                "numCpu": config.hardware.numCPU,
                "numCoresPerSocket": config.hardware.numCoresPerSocket,
                "memoryMB": config.hardware.memoryMB,
                "template": config.template,
                "networkDevices": vmNets,
                "diskDevices": vmDisks
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
    def list(assetId, templatesAlso: bool = True) -> List[dict]:
        virtualmachines = list()

        try:
            for v in Backend.oVirtualMachines(assetId):
                if templatesAlso or not v.config.template:
                    data = VmwareHelper.vmwareObjToDict(v)
                    virtualmachines.append(data)

            return virtualmachines
        except Exception as e:
            raise e
