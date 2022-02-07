from typing import List
from pyVmomi import vim

from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.VMFolder import VMFolder
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
        try:
            # Perform some preliminary checks.
            if not self.__isClusterValid(data["datacenterId"], data["clusterId"]):
                raise CustomException(status=400, payload={"VMware": "clusterId not found in this datacenter."})

            raise Exception
            # @todo.

            cluster = Cluster(self.assetId, clusterObj._GetMoId())
            cluDatastoreObjList = cluster.oDatastores()
            for d in cluDatastoreObjList:
                if data["datastoreId"] == d._GetMoId(): # VMware pvmomi method.
                    datastoreObj = d
            if not datastoreObj:
                raise CustomException(status=400, payload={"VMware": "datastoreId not found attached to this cluster."})

            cluNetworkObjList = cluster.oNetworks()
            for n in cluNetworkObjList:
                if data["networkId"] == n._GetMoId():
                    networkObj = n
            if not networkObj:
                raise CustomException(status=400, payload={"VMware": "networkId not found attached to this cluster."})

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



    def info(self) -> dict:
        vmDisks = list()
        vmNets = list()

        try:
            config = self.oVirtualMachine.config
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
        datacenter = Datacenter(self.assetId, datacenterMoId)

        datacenter.loadClusters()
        for cluster in datacenter.clusters:
            if clusterMoId == cluster.moId:
                # @todo: need to perform some checks on cluster?
                return True

        return False



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
