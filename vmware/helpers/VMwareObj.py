from pyVmomi import vim, vmodl
from vmware.helpers.Log import Log


# Helpers to make some operations on vmware pyVmomi objects.
class VMwareObj:
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The moId is the VMware Managed Object Id. Can be obtained from the "_moId" property of a managed object.
        self.assetId = int(assetId)
        self.moId = moId



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def vmwareObjToDict(vmwareObj) -> dict:
        try:
            return dict({
                "moId": vmwareObj._GetMoId(),
                "name": vmwareObj.name
        })

        except Exception as e:
            raise e



    @staticmethod
    def getDjangoObjFromVMware(vmwareObj, assetId, DjangoCLass) -> dict:
        try:
            newObj = DjangoCLass(assetId, vmwareObj._GetMoId())
            newObj.vmwareObj = vmwareObj
            return newObj

        except Exception as e:
            raise e

