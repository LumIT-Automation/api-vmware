from vmware.models.VMware.backend.Task import Task as Backend


class Task(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            info = {
                "entityName": self.oTask.info.entityName,
                "entity_moId": self.oTask.info.entity._GetMoId(),
                "queueTime": str(self.oTask.info.queueTime),
                "startTime": str(self.oTask.info.startTime),
                "progress": self.oTask.info.progress,
                "state": self.oTask.info.state
            }
            return info

        except Exception as e:
            raise e



    def cancel(self) -> None:
        try:
            self.oCancel()

        except Exception as e:
            raise e



    def setDescription(self, description: str = "") -> None:
        try:
            self.oSetDescription(description)

        except Exception as e:
            raise e

