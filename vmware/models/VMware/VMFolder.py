from pyVmomi import vim, vmodl
from pprint import pprint

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log


class VMFolder:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def folderTree(self, silent: bool = None) -> list:
        treeList = list()
        vClient = None

        try:
            vmware = Asset(self.assetId)
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
                treeList.append(self.__folderTree(parentFolder, tree))

            return treeList

        except Exception as e:
            raise e

        finally:
            if vClient and hasattr(vClient, 'content'):
                vClient.disconnect()

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

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
            Log.log(folder._moId, 'TTTTT')
            children = folder.childEntity
            for child in children:
                if isinstance(child, vim.Folder):
                    subTree = {
                        child._moId: {
                            "name": child.name,
                            "subFolders": {}
                        }
                    }
                    tree[folder._moId]["subFolders"].update(subTree)
                    VMFolder.__folderTree(child, subTree)

        return tree

