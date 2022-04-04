from vmware.models.VMware.Datastore import Datastore


class VirtualMachineDatastore:
    # Virtual machine disk / attached datastore.

    def __init__(self, assetId: int, datastoreMoId: str, diskLabel: str, diskSize: float, deviceType: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.datastore: Datastore = Datastore(assetId, datastoreMoId)
        self.label = diskLabel
        self.size = diskSize
        self.deviceType = deviceType



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self):
        try:
            return {
                "datastoreMoId": self.datastore.moId,
                "label": self.label,
                "sizeMB": self.size,
                "deviceType": self.deviceType
            }
        except Exception as e:
            raise e
