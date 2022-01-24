from pyVmomi import vim, vmodl

from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.VMFolder import VMFolder

from vmware.helpers.Log import Log
from vmware.helpers.VmwareHelper import VmwareHelper

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
            cluDatastoreObjList = cluster.listDatastoresObjects()
            for d in cluDatastoreObjList:
                if data["datastoreId"] == d._GetMoId(): # VMware pvmomi method.
                    datastoreObj = d
            if not datastoreObj:
                raise CustomException(status=400, payload={"VMware": "datastoreId not found attached to this cluster."})

            cluNetworkObjList = cluster.listNetworksObjects()
            for n in cluNetworkObjList:
                if data["networkId"] == n._GetMoId():
                    networkObj = n
            if not networkObj:
                raise CustomException(status=400, payload={"VMware": "networkId not found attached to this cluster."})

            vmFolder = VMFolder(self.assetId, data["vmFolderId"])
            vmFolder.getVMwareObject()
            vmFolderObj = vmFolder.vmwareObj

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
            task = self.vmwareObj.Clone(folder=vmFolderObj, name=data["vmName"], spec=cloneSpec)

            return dict({
                "task": task._GetMoId()
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = True) -> dict:
        tList = []
        try:
            tObjList = VirtualMachineTemplate.listTemplatesOnlyObjects(assetId, silent)

            for t in tObjList:
                tList.append(VmwareHelper.vmwareObjToDict(t))

            return dict({
                "items": tList
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter templates (not regular virtual machines) pyVmomi objects list.
    def listTemplatesOnlyObjects(assetId, silent: bool = True) -> list:
        tObjList = list()
        try:
            objList = VirtualMachine.listVirtualMachinesObjects(assetId, silent)
            for obj in objList:
                if obj.config.template:
                    tObjList.append(obj)

            return tObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __isVmTemplate(self):
        config = self.getVirtualMachineConfigObject()
        return config.template