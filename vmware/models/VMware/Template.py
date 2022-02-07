from typing import List
from pyVmomi import vim


from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend
from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.VMFolder import VMFolder

from vmware.helpers.vmware.VmwareHelper import VmwareHelper

from vmware.helpers.Exception import CustomException



class VirtualMachineTemplate(VirtualMachine):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        if not self.__isVmTemplate():
            raise CustomException(status=400, payload={"VMware": "this object is not a virtual machine template."})

        info = super().info()
        return info



    def deployVM(self, data: dict) -> dict:
        clusterObj = None
        datastoreObj = None
        networkObj = None

        try:
            datacenter = Datacenter(self.assetId, data["datacenterId"])

            dcClusterObjList = datacenter.listComputeResourcesObjects()
            for c in dcClusterObjList:
                if data["clusterId"] == c._GetMoId():
                    clusterObj = c
            if not clusterObj:
                raise CustomException(status=400, payload={"VMware": "clusterId not found in this datacenter."})

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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId) -> List[dict]:
        virtualmachines = list()

        try:
            for v in Backend.oVirtualMachines(assetId):
                if v.config.template:
                    data = VmwareHelper.vmwareObjToDict(v)
                    virtualmachines.append(data)

            return virtualmachines
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __isVmTemplate(self):
        return self.oVirtualMachine.config.template