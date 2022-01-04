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
    def list(assetId, silent: bool = True) -> dict:
        vms = []
        try:
            vmObjList = VirtualMachine.listVirtualMachinesObjects(assetId, silent)

            for vm in vmObjList:
                vms.append(VMwareObj.vmwareObjToDict(vm))

            return dict({
                "items": vms
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter datacenter pyVmomi objects list.
    def listVirtualMachinesObjects(assetId, silent: bool = True) -> list:
        vmObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            vmObjList = vClient.getAllObjs([vim.VirtualMachine])

            return vmObjList

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

