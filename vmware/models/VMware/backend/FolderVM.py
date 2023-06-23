from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class FolderVM(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oVMFolder = self.__oVMFolderLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oContents(self) -> list:
        try:
            return self.oVMFolder.childEntity
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oVMFolders(assetId) -> list:
        oVMFoldersList = list()

        try:
            vmFoldersList = VmwareHandler().getObjects(assetId=assetId, vimType=vim.Folder)
            for f in vmFoldersList:
                if f.childType == ['Folder', 'VirtualMachine', 'VirtualApp']:
                    oVMFoldersList.append(f)

            return oVMFoldersList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oVMFolderLoad(self):
        try:
            return self.getObjects(assetId=self.assetId, vimType=vim.Folder, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "Cannot load resource."})
