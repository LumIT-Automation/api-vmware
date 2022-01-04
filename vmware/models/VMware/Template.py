from pyVmomi import vim, vmodl

from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class VirtualMachineTemplate(VirtualMachine):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################



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
