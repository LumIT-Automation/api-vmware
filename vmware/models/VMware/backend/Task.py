from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler

from vmware.helpers.Log import Log

class Task(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oTask = self.__oTaskLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oCancel(self) -> None:
        try:
            self.oTask.CancelTask()
        except Exception as e:
            raise e



    def oSetDescription(self, description: str = "") -> None:
        try:
            self.oTask.SetTaskDescription(description)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oTaskLoad(self):
        try:
            taskManager = self._getSubContent('taskManager')
            for task in taskManager.recentTask:
                if task.info.key == self.moId:
                    return task
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
        except Exception as e:
            raise e
