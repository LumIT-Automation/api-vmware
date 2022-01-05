from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class VMwareDjangoObj:
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The moId is the VMware Managed Object Id.
        # Can be obtained from the _GetMoId() method or from the "_moId" property of a managed object.
        self.assetId = int(assetId)
        self.moId = moId
        self.vmwareObj = None



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def connectToAssetAndGetContent(self, silent: bool = True):
        try:
            vmware = Asset(self.assetId)
            vmwareInfo = vmware.info()
            dataConnection = vmwareInfo["dataConnection"]

            vClient = VmwareSupplicant(dataConnection, silent)
            vClient.getContent()

            return vClient

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def connectToAssetAndGetContentStatic(assetId, silent: bool = True):
        try:
            vmware = Asset(assetId)
            vmwareInfo = vmware.info()
            dataConnection = vmwareInfo["dataConnection"]

            vClient = VmwareSupplicant(dataConnection, silent)
            vClient.getContent()

            return vClient

        except Exception as e:
            raise e


#################################### AMBIGUO
    @staticmethod
    def vmwareObjToDict(vmwareObj) -> dict:
        try:
            return dict({
                "moId": vmwareObj._GetMoId(),
                "name": vmwareObj.name
        })

        except Exception as e:
            raise e


    ####################################################################################################################
    # Protected methods
    ####################################################################################################################

    def _getVMwareObject(self, vimType: str, refresh: bool = False, silent: bool = True) -> object:
        if not self.vmwareObj or refresh:
            try:
                vClient = self.connectToAssetAndGetContent(silent)
                objList = vClient.getAllObjs([vimType])
                for obj in objList:
                    if obj._GetMoId() == self.moId:
                        self.vmwareObj = obj

            except Exception as e:
                raise e
        else:
            pass


