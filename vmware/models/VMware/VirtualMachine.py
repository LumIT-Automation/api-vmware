from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class VirtualMachine(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        clusters = []
        datastores = []
        networks = []
        try:
            # each element of computeResourcesList is a set containing a vmware ClusterComputeResource object.
            for cr in computeResourcesList:
                for c in cr:
                    clusters.append(VMwareObj.vmwareObjToDict(c))

            # each element of dsList is a set containing a vmware Datastore object.
            for ds in dsList:
                for d in ds:
                    datastores.append(VMwareObj.vmwareObjToDict(d))

            # each element of computeResources is a set containing a vmware Network object.
            for net in nList:
                for n in net:
                    networks.append(VMwareObj.vmwareObjToDict(n))

            return dict({
                "clusters": clusters,
                "datastores": datastores,
                "networks": networks
            })

        except Exception as e:
            raise e











    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def listVMs(assetId, silent: bool = True) -> dict:
        vmList = []
        try:
            vmObjList = VirtualMachine.listVirtualMachinesOnlyObjects(assetId, silent)

            for vm in vmObjList:
                vmList.append(VMwareObj.vmwareObjToDict(vm))

            return dict({
                "items": vmList
            })

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter datacenters list.
    def listTemplates(assetId, silent: bool = True) -> dict:
        tList = []
        try:
            tObjList = VirtualMachine.listTemplatesOnlyObjects(assetId, silent)

            for t in tObjList:
                tList.append(VMwareObj.vmwareObjToDict(t))

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



    @staticmethod
    # vCenter virtual machines (not templates) pyVmomi objects list.
    def listVirtualMachinesOnlyObjects(assetId, silent: bool = True) -> list:
        vmObjList = list()
        try:
            objList = VirtualMachine.listVirtualMachinesObjects(assetId, silent)
            for obj in objList:
                if not obj.config.template:
                    vmObjList.append(obj)

            return vmObjList

        except Exception as e:
            raise e



    @staticmethod
    # vCenter virtual machines and templates pyVmomi objects list.
    def listVirtualMachinesObjects(assetId, silent: bool = True) -> list:
        objList = list()
        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            objList = vClient.getAllObjs([vim.VirtualMachine])
            return objList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        try:
            self._getVMwareObject(vim.VirtualMachine, refresh, silent)

        except Exception as e:
            raise e

