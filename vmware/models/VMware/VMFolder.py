from pyVmomi import vim, vmodl
from vmware.models.VMwareObj import VMwareObj

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class VMFolder(VMwareObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    # For a vCenter folder get the list of the parent folders.
    def parentList(self, silent: bool = None) -> list:
        parentList = list()
        vClient = None

        try:
            vClient = self.connectToAsset(silent)
            allFolders = vClient.getAllObjs([vim.Folder])

            moId = self.moId
            folder = None
            while True:
                for f in allFolders:
                    if f._moId == moId:
                        folder = f.parent
                        moId = f.parent._moId
                        parentList.insert(0, moId)
                        break

                if not isinstance(folder, vim.Folder):
                    break

            return parentList

        except Exception as e:
            raise e

        #finally:
        #    if vClient and hasattr(vClient, 'content'):
        #        vClient.disconnect()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    # vCenter folders tree built using pvmomi.
    @staticmethod
    def folderTree(assetId, silent: bool = None) -> list:
        treeList = list()
        vClient = None
        datacenters = []

        # TODO: move in Datacenter.py
        def datacenterList(folder: vim.Folder, dcList: []) -> list:
            children = folder.childEntity
            for c in children:
                if isinstance(c, vim.Datacenter):
                    dcList.append(c)
                elif isinstance(c, vim.Folder):
                    datacenterList(c, dcList)

            return dcList

        try:
            vClient = VMwareObj.connectToAssetStatic(assetId, silent)
            rootFolder = vClient.content.rootFolder
            datacenters = datacenterList(rootFolder, datacenters)

            for dc in datacenters:
                if isinstance(dc, vim.Datacenter):
                    parentFolder = dc.vmFolder
                    tree = {
                        parentFolder._moId: {
                            "name": dc.name,
                            "subFolders": {}
                        }
                    }
                    treeList.append(VMFolder.__folderTree(parentFolder, tree))

            return treeList

        except Exception as e:
            raise e

        #finally:
        #    if vClient and hasattr(vClient, 'content'):
        #        vClient.disconnect()



    @staticmethod
    # Plain vCenter folders list using pvmomi (a rest api call can be used alse for this onw).
    def list(assetId, silent: bool = None) -> dict:
        data = {
            "data": []
        }
        vClient = None

        try:
            vClient = VMwareObj.connectToAssetStatic(assetId, silent)
            allFolders = vClient.getAllObjs([vim.Folder])

            for f in allFolders:
                of = {
                    "moId": f._moId,
                    "name": f.name
                }
                data["data"].append(of)

            return data

        except Exception as e:
            raise e

        #finally:
        #    if vClient and hasattr(vClient, 'content'):
        #        vClient.disconnect()



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __folderTree(folder, tree: {}):
        if isinstance(folder, vim.Folder):
            children = folder.childEntity
            for child in children:
                if isinstance(child, vim.Folder):
                    # _moId == Managed object Id.
                    subTree = {
                        child._moId: {
                            "name": child.name,
                            "subFolders": {}
                        }
                    }
                    tree[folder._moId]["subFolders"].update(subTree)
                    VMFolder.__folderTree(child, subTree)

        return tree