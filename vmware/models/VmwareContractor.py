from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class VmwareContractor:
    def __init__(self, assetId: int, moId: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The moId is the VMware Managed Object Id.
        # Can be obtained from the _GetMoId() method or from the "_moId" property of a managed object.
        self.assetId = int(assetId)
        self.moId = moId
        self.oCluster = None



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getContainer(self, vimType: str) -> dict:
        try:
            vClient = self.connectToAssetAndGetContent()
            return vClient.getAllObjs([vimType])
        except Exception as e:
            raise e




    def connectToAssetAndGetContent(self) -> VmwareSupplicant:
        try:
            vClient = VmwareSupplicant(Asset(self.assetId).dataConnection)
            vClient.getContent()

            return vClient
        except Exception as e:
            raise e





    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def connectToAssetAndGetContentStatic(assetId):
        try:
            vClient = VmwareSupplicant(
                Asset(assetId).dataConnection
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


    # OLD ################################################################
    def _getContainer(self, vimType: str) -> None:
        try:
            vClient = self.connectToAssetAndGetContent()
            objList = vClient.getAllObjs([vimType])

            for obj, v in objList.items():
                if obj._GetMoId() == self.moId:
                    self.oCluster = obj
        except Exception as e:
            raise e

