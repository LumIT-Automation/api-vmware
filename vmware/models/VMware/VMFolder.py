from pyVmomi import vim, vmodl
from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class VMFolder(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    # For a vCenter virtual machine folder get the list of the virtual machines and vApps.
    def info(self, silent: bool = True) -> dict:
        o = {
            "vmList": [],
            "vAppList": []
        }

        try:
            [ vmList, vAppList ] = self.listVMObjects()
            for vm in vmList:
                o["vmList"].append(VMwareObj.vmwareObjToDict(vm))
            for app in vAppList:
                o["vAppList"].append(VMwareObj.vmwareObjToDict(app))

            return o

        except Exception as e:
            raise e



    # For a vCenter virtual machine folder get the plain list of the parent folders moIds.
    def parentList(self, silent: bool = True) -> list:
        parentList = list()
        vClient = None

        try:
            vClient = self.connectToAssetAndGetContent(silent)
            allFolders = vClient.getAllObjs([vim.Folder])

            moId = self.moId
            folder = None
            while True:
                for f in allFolders:
                    if f._GetMoId() == moId:
                        folder = f.parent
                        moId = f.parent._GetMoId()
                        parentList.insert(0, moId)
                        break

                if not isinstance(folder, vim.Folder):
                    break

            return parentList

        except Exception as e:
            raise e



    def listVMObjects(self) -> list:
        vmList = list()
        vAppList = list()
        try:
            self.getVMwareObject()
            children = self.vmwareObj.childEntity
            for child in children:
                if isinstance(child, vim.VirtualMachine):
                    vmList.append(child)
                if isinstance(child, vim.VirtualApp):
                    vAppList.append(child)

            return [ vmList, vAppList]

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        try:
            self._getVMwareObject(vim.Folder, refresh, silent)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    # vCenter folders tree built using pvmomi.
    @staticmethod
    def folderTree(assetId, silent: bool = True) -> list:
        treeList = list()

        try:
            from vmware.models.VMware.Datacenter import Datacenter
            datacenters = Datacenter.listDatacentersObjects(assetId)

            for dc in datacenters:
                if isinstance(dc, vim.Datacenter):
                    parentFolder = dc.vmFolder
                    tree = {
                        parentFolder._GetMoId(): {
                            "name": dc.name,
                            "subFolders": {}
                        }
                    }
                    treeList.append(VMFolder.__folderTree(parentFolder, tree))

            return treeList

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter networks list by default, otherwise show the folderTree output.
    def list(assetId, formatTree: bool = False, silent: bool = True) -> dict:
        folders = []
        if formatTree:
            folders = VMFolder.folderTree(assetId, silent)
        else:
            try:
                vmFoldersObjList = VMFolder.listVMFoldersObjects(assetId, silent)
                for f in vmFoldersObjList:
                    folders.append(VMwareObj.vmwareObjToDict(f))


            except Exception as e:
                raise e

        return dict({
            "items": folders
        })



    @staticmethod
    # vCenter networks pyVmomi objects list.
    def listVMFoldersObjects(assetId, silent: bool = True) -> list:
        vmFoldersObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            vmFoldersObjList = vClient.getAllObjs([vim.Folder])

            return vmFoldersObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __folderTree(folderObj, tree: {}):
        if isinstance(folderObj, vim.Folder):
            children = folderObj.childEntity
            for child in children:
                if isinstance(child, vim.Folder):
                    # _GetMoId() == obj._moId == Managed object Id.
                    subTree = {
                        child._GetMoId(): {
                            "name": child.name,
                            "subFolders": {}
                        }
                    }
                    tree[folderObj._GetMoId()]["subFolders"].update(subTree)
                    VMFolder.__folderTree(child, subTree)

        return tree


