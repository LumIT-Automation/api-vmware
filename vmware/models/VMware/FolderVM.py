from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.FolderVM import FolderVM as Backend
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class FolderVM(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVMFolder.name

        self.folders: List[FolderVM] = []
        self.virtualmachines: List[VirtualMachine] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadContents(self, loadVms: bool = True) -> None:
        try:
            for o in self.oContents():
                objData = VmwareHelper.getInfo(o)
                if isinstance(o, vim.Folder):
                    self.folders.append(
                        FolderVM(self.assetId, objData["moId"])
                    )

                if loadVms:
                    if isinstance(o, vim.VirtualMachine):
                        self.virtualmachines.append(
                            VirtualMachine(self.assetId, objData["moId"])
                        )
        except Exception as e:
            raise e



    def info(self, loadVms: bool = True) -> dict:
        folders = list()
        vms = list()

        try:
            self.loadContents(loadVms)
            for f in self.folders:
                folders.append(
                    FolderVM.__cleanup("", f.info(loadVms))
                )

            if loadVms:
                for v in self.virtualmachines:
                    vms.append(
                        FolderVM.__cleanup("info.vm", v.info(False))
                    )

            out = {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.name,
                "folders": folders
            }

            if loadVms:
                out.update({"virtualmachines": vms})

            return out
        except Exception as e:
            raise e



    # Plain list of the parent folders.
    def parentList(self) -> list:
        folder = self.oVMFolder
        parentList = list()
        try:
            while True:
                folder = folder.parent
                moId = folder._GetMoId()
                parentList.insert(0, moId)
                if not isinstance(folder, vim.Folder):
                    break

            return parentList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    # Composition version
    @staticmethod
    def folderTreeComp(assetId) -> list:
        treeList = list()
        try:
            datacenters = Datacenter.oDatacenters(assetId)
            for dc in datacenters:
                rootFolder = FolderVM(assetId, dc.vmFolder._GetMoId())

                subTree = rootFolder.info(False) # recursive by composition.
                treeList.append(subTree)

            return treeList
        except Exception as e:
            raise e



    # Quick version
    @staticmethod
    def foldersTree(assetId: int, folderMoIdList: list = None) -> list:
        folderMoIdList = [] if folderMoIdList is None else folderMoIdList
        treeList = list()
        try:
            if not folderMoIdList:
                datacenters = Datacenter.oDatacenters(assetId)
                for dc in datacenters:
                    folderMoIdList.append(dc.vmFolder._GetMoId())

            for folderMoId in folderMoIdList:
                treeList.extend(FolderVM.folderTree(assetId, folderMoId))

            return treeList
        except Exception as e:
            raise e



    # Quick version
    @staticmethod
    def folderTree(assetId: int, folderMoId: str) -> list:
        treeList = list()
        try:
            parentFolder = FolderVM(assetId, folderMoId).oVMFolder
            tree = {
                "assetId": assetId,
                "moId": parentFolder._GetMoId(),
                "name": parentFolder.name,
                "folders": []
            }
            treeList.append(FolderVM.__folderTree(assetId, parentFolder, tree))

            return treeList
        except Exception as e:
            raise e



    # Recursive. Get all the "moId" element of a folder tree and put them in a list (order doesn't matter).
    @staticmethod
    def treeToSet(treeElements: list, moIdSet: set = None) -> list:
        moIdSet = set() if moIdSet is None else moIdSet
        for el in treeElements:
            moIdSet.add(el["moId"])
            if el["folders"]:
                FolderVM.treeToSet(el["folders"], moIdSet)

        return moIdSet



    @staticmethod
    def purgeOverlapTrees(treesList: list) -> list:
        try:
            treesDict = dict()
            for tree in treesList:
                treesDict[tree["moId"]] = FolderVM.treeToSet(tree["folders"]) # Convert the trees to plain lists. Order doesn't matter.

            for parent in treesDict.keys():
                for subTree in treesDict.values():
                    if parent in subTree: # The moId of a parent folder was found in another subtree.
                        for item in treesList:
                            if item["moId"] == parent: # Get the index of the element and remove it.
                                index = treesList.index(item)
                                treesList.pop(index)

            return treesList
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId, formatTree: bool = False, folderMoId: str = "") -> list:
        folders = list()

        if formatTree:
            folders = FolderVM.folderTree(assetId, folderMoId)
        else:
            try:
                for f in Backend.oVMFolders(assetId):
                    folders.append(VmwareHelper.getInfo(f))

            except Exception as e:
                raise e

        return folders



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __folderTree(assetId: int, oVMFolder: object, tree: dict):
        if isinstance(oVMFolder, vim.Folder):
            if not "folders" in tree:
                tree["folders"] = []
            children = oVMFolder.childEntity
            for child in children:
                if isinstance(child, vim.Folder):
                    subTree = {
                        "assetId": assetId,
                        "moId": child._GetMoId(),
                        "name": child.name,
                        "folders": []
                    }
                    tree["folders"].append(subTree)
                    FolderVM.__folderTree(assetId, child, subTree)
        return tree



    @staticmethod
    def __cleanup(oType: str, o: dict):
        try:
            if oType == "info.vm":
                if not o["networkDevices"]:
                    del (o["networkDevices"])
                if not o["diskDevices"]:
                    del (o["diskDevices"])

            if oType == "output":
                if not o["virtualmachines"]:
                    del (o["virtualmachines"])
        except Exception:
            pass

        return o
