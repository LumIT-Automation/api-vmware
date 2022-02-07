from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.VMFolder import VMFolder as Backend
from vmware.models.VMware.Datacenter import Datacenter

from vmware.helpers.vmware.VmwareHelper import VmwareHelper

class VMFolder(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVMFolder.name

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
                o["vmList"].append(VmwareHelper.vmwareObjToDict(vm))
            for app in vAppList:
                o["vAppList"].append(VmwareHelper.vmwareObjToDict(app))

            return o

        except Exception as e:
            raise e



    # For a vCenter virtual machine folder get the plain list of the parent folders moIds.
    def parentList(self, silent: bool = True) -> list:
        parentList = list()

        try:

            allFolders = Backend.oVMFolders(self.assetId)

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
            self.oVMFolder
            children = self.oVMFolder.childEntity
            for child in children:
                if isinstance(child, vim.VirtualMachine):
                    vmList.append(child)
                if isinstance(child, vim.VirtualApp):
                    vAppList.append(child)

            return [ vmList, vAppList]

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    # vCenter folders tree built using pvmomi.
    @staticmethod
    def folderTree(assetId) -> list:
        treeList = list()

        try:
            datacenters = Datacenter.oDatacenters(assetId)

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
    # Plain vCenter vmirtual machine folders list by default, otherwise show the folderTree output.
    def list(assetId, formatTree: bool = False) -> dict:
        folders = list()

        if formatTree:
            folders = VMFolder.folderTree(assetId)
        else:
            try:
                for f in Backend.oVMFolders(assetId):
                    data = VmwareHelper.vmwareObjToDict(f)
                    folders.append(data)

            except Exception as e:
                raise e

        return folders



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


