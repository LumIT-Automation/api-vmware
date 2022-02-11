from vmware.models.VMware.Datastore import Datastore


class VirtualMachineDatastore:
    # Virtual machine disk / attached datastore.

    def __init__(self, assetId: int, datastoreMoId: str, diskLabel: str, diskSize: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.datastore: Datastore = Datastore(assetId, datastoreMoId)
        self.label = diskLabel
        self.size = diskSize



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self):
        try:
            return {
                "datastoreMoId": self.datastore.moId,
                "disk": self.label,
                "size": self.size
            }
        except Exception as e:
            raise e
