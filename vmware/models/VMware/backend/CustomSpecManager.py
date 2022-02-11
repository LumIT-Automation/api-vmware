from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log

class CustomSpecManager(VmwareHandler):
    def __init__(self, assetId: int, moId: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.oCustomSpecManager = self.__oCustomSpecManagerLoad()
        self.moId = self.oCustomSpecManager._GetMoId()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oCustomSpec(self, name) -> object:
        try:
            return self.oCustomSpecManager.GetCustomizationSpec(name=name)
        except Exception as e:
            raise e



    def oCustomSpecs(self) -> list:
        try:
            return self.oCustomSpecManager.info
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oCustomSpecManagerLoad(self):
        try:
            if not self.content:
                self._fetchContent()
            return self.content.customizationSpecManager
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
