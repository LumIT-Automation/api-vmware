from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.VirtualMachineFolder import VirtualMachineFolder as Backend
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class VirtualMachineFolder(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVMFolder.name

        self.folders: List[VirtualMachineFolder] = []
        self.virtualmachines: List[VirtualMachine] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadContents(self, loadVms: bool = True) -> None:
        try:
            for o in self.oContents():
                objData = VmwareHelper.vmwareObjToDict(o)
                if isinstance(o, vim.Folder):
                    self.folders.append(
                        VirtualMachineFolder(self.assetId, objData["moId"])
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
                    VirtualMachineFolder.__cleanup("", f.info(loadVms))
                )

            if loadVms:
                for v in self.virtualmachines:
                    vms.append(
                        VirtualMachineFolder.__cleanup("info.vm", v.info(False))
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
        moId = self.moId
        folder = None
        parentList = list()

        try:
            allFolders = Backend.oVMFolders(self.assetId)

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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def folderTree(assetId) -> list:
        treeList = list()
        try:
            datacenters = Datacenter.oDatacenters(assetId)
            for dc in datacenters:
                rootFolder = VirtualMachineFolder(assetId, dc.vmFolder._GetMoId())

                subTree = rootFolder.info(False) # recursive by composition.
                treeList.append(subTree)

            return treeList
        except Exception as e:
            raise e



    @staticmethod
    def folderTreeQuick(assetId) -> list:
        treeList = list()

        try:
            datacenters = Datacenter.oDatacenters(assetId)

            for dc in datacenters:
                if isinstance(dc, vim.Datacenter):
                    parentFolder = dc.vmFolder
                    tree = {
                        parentFolder._GetMoId(): {
                            "name": dc.name,
                            "folders": {}
                        }
                    }
                    treeList.append(VirtualMachineFolder.__folderTree(parentFolder, tree))

            return treeList

        except Exception as e:
            raise e



    @staticmethod
    def list(assetId, formatTree: bool = False) -> list:
        folders = list()

        if formatTree:
            folders = VirtualMachineFolder.folderTree(assetId)
        else:
            try:
                for f in Backend.oVMFolders(assetId):
                    folders.append(VmwareHelper.vmwareObjToDict(f))

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
                            "folders": {}
                        }
                    }
                    tree[folderObj._GetMoId()]["folders"].update(subTree)
                    VirtualMachineFolder.__folderTree(child, subTree)

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
