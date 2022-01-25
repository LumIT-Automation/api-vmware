from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class VmwareContractor:
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The moId is the VMware Managed Object Id.
        # Can be obtained from the _GetMoId() method or from the "_moId" property of a managed object.
        self.assetId = int(assetId)
        self.moId = moId
        self.client = None



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def connectToAssetAndGetContent(self):
        try:
            vClient = VmwareSupplicant(
                Asset(self.assetId).dataConnection
            )
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
            vClient = VmwareSupplicant(
                Asset(assetId).dataConnection,
                silent
            )
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

    def _getContract(self, vimType: str) -> None:
        try:
            vClient = self.connectToAssetAndGetContent()
            objList = vClient.getAllObjs([vimType])
            for obj, v in objList.items():
                if obj._GetMoId() == self.moId:
                    self.client = obj
        except Exception as e:
            raise e

