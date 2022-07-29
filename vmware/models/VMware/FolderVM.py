from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.FolderVM import FolderVM as Backend
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.VMware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class FolderVM(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVMFolder.name

        self.children: List[FolderVM] = []
        self.virtualmachines: List[VirtualMachine] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadContents(self, loadVms: bool = True) -> None:
        try:
            for o in self.oContents():
                objData = VmwareHelper.getInfo(o)
                if isinstance(o, vim.Folder):
                    self.children.append(
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
        children = list()
        vms = list()

        try:
            self.loadContents(loadVms)
            for f in self.children:
                children.append(
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
                "children": children
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



    # Plain list of the parent folders.
    def parentDatacenter(self) -> list:
        folder = self.oVMFolder
        try:
            while True:
                folder = folder.parent
                if isinstance(folder, vim.Datacenter):
                    return [ folder._GetMoId(), folder.name ]

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def foldersTreeComp(assetId) -> list:
        # Composition version. Slower.

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



    @staticmethod
    def foldersTreeQuick(assetId: int, folderMoIdList: list = None) -> list:
        folderMoIdList = [] if folderMoIdList is None else folderMoIdList
        treeList = list()
        folderDataList = list()
        try:
            if not folderMoIdList:
                datacenters = Datacenter.oDatacenters(assetId)
                for dc in datacenters:
                    fData = [dc.vmFolder._GetMoId(), dc._GetMoId(), dc.name] # [folder.moId, datacenter.moId, datacenter.name].
                    folderDataList.append(fData)
            else:
                for folderMoId in folderMoIdList:
                    folder = FolderVM(assetId, folderMoId)
                    datacenterData = folder.parentDatacenter() # [datacenter.moId, datacenter.name].
                    folderDataList.append([folderMoId, datacenterData[0], datacenterData[1]])

            # For each tree/subtree, append the datacenter info to the parent folder data.
            for folderData in folderDataList:
                tree = FolderVM.folderTreeQuick(assetId, folderData[0])
                if not hasattr(tree[0], 'datacenterMoId'):
                    tree[0]['datacenterMoId'] = folderData[1]
                    tree[0]['datacenterName'] = folderData[2]
                treeList.extend(tree)

            return treeList
        except Exception as e:
            raise e



    @staticmethod
    def folderTreeQuick(assetId: int, folderMoId: str) -> list:
        treeList = list()
        try:
            parentFolder = FolderVM(assetId, folderMoId).oVMFolder
            tree = {
                "assetId": assetId,
                "moId": parentFolder._GetMoId(),
                "key": parentFolder._GetMoId(), # workaround for the Ant Design shitty tree object.
                "name": parentFolder.name,
                "title": parentFolder.name, # workaround for the Ant Design shitty tree object.
                "children": []
            }
            treeList.append(FolderVM.__folderTree(assetId, parentFolder, tree))

            return treeList
        except Exception as e:
            raise e



    @staticmethod
    def treeToSet(treeElements: list, moIdSet: set = None) -> set:
        # Recursive. Get all the "moId" element of a folder tree and put them in a set (order doesn't matter).
        moIdSet = set() if moIdSet is None else moIdSet

        for el in treeElements:
            moIdSet.add(el["moId"])
            if el["children"]:
                FolderVM.treeToSet(el["children"], moIdSet)

        return moIdSet



    @staticmethod
    def purgeOverlapTrees(treesList: list) -> list:
        try:
            treesDict = dict()
            for tree in treesList:
                treesDict[tree["moId"]] = FolderVM.treeToSet(tree["children"]) # convert the trees to plain lists. Order doesn't matter.

            for parent in treesDict.keys():
                for subTree in treesDict.values():
                    if parent in subTree: # the moId of a parent folder was found in another subtree.
                        for item in treesList:
                            if item["moId"] == parent: # get the index of the element and remove it.
                                index = treesList.index(item)
                                treesList.pop(index)

            return treesList
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId, formatTree: bool = False, folderMoId: str = "") -> list:
        folders = list()

        if formatTree:
            folders = FolderVM.folderTreeQuick(assetId, folderMoId)
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
            if "children" not in tree:
                tree["children"] = []
            children = oVMFolder.childEntity
            for child in children:
                if isinstance(child, vim.Folder):
                    subTree = {
                        "assetId": assetId,
                        "moId": child._GetMoId(),
                        "key": child._GetMoId(), # workaround for the Ant Design shitty tree object.
                        "name": child.name,
                        "title": child.name, # workaround for the Ant Design shitty tree object.
                        "children": []
                    }
                    tree["children"].append(subTree)
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
