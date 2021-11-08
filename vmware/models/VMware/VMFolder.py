from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class VMFolder:
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        # The moId is the VMware Managed Object Id. Can be obtained from the "_moId" property of a managed object.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def parentList(self, silent: bool = None) -> list:
        parentList = list()
        vClient = None

        try:
            vmware = Asset(self.assetId)
            dataConnection = vmware.vmwareDataConnection()

            vClient = VmwareSupplicant(dataConnection, silent)
            vClient.getContent()

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

        finally:
            if vClient and hasattr(vClient, 'content'):
                vClient.disconnect()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def folderTree(assetId, silent: bool = None) -> list:
        treeList = list()
        vClient = None

        try:
            vmware = Asset(assetId)
            dataConnection = vmware.vmwareDataConnection()

            vClient = VmwareSupplicant(dataConnection, silent)
            vClient.getContent()

            datacenters = vClient.content.rootFolder.childEntity  # TODO: this should be performed by the datacenter class.
            for dc in datacenters:
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

        finally:
            if vClient and hasattr(vClient, 'content'):
                vClient.disconnect()



    # Plain folders list using rest api, not pvmomi.
    @staticmethod
    def list(assetId: int) -> dict:
        o = dict()

        try:
            vmware = Asset(assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/auth/vmFolder/",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            o["data"] = api.get()
        except Exception as e:
            raise e

        return o



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