from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.vmware.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log


class VmwareHandler:
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

    def getObjects(self, vimType: str) -> dict:
        try:
            supplicant = VmwareSupplicant(Asset(self.assetId).connectionData)
            return supplicant.getObjects([vimType])
        except Exception as e:
            raise e
