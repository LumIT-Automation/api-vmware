from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.VMFolder import VMFolder as Backend
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class VMFolder(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVMFolder.name

        self.folders: List[VMFolder] = []
        self.virtualmachines: List[VirtualMachine] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadContents(self, loadSubFolders: bool = True, loadVirtualMachines: bool = True) -> None:
        try:
            for o in self.oContents():
                objData = VmwareHelper.vmwareObjToDict(o)

                if loadSubFolders:
                    if isinstance(o, vim.Folder):
                        self.folders.append(
                            VMFolder(self.assetId, objData["moId"])
                        )
                if loadVirtualMachines:
                    if isinstance(o, vim.VirtualMachine):
                        self.virtualmachines.append(
                            VirtualMachine(self.assetId, objData["moId"])
                        )
        except Exception as e:
            raise e



    # For a vCenter virtual machine folder get the list of the virtual machines and vApps.
    def info(self, getSubFolders: bool = True, getVirtualmachines: bool = True) -> dict:
        subFolders = list()
        vms = list()

        try:
            self.loadContents(getSubFolders, getVirtualmachines)
            if getSubFolders:
                for f in self.folders:
                    subFolders.append(
                        VMFolder.__cleanup(
                            "folder",
                            f.info(getSubFolders, getVirtualmachines)
                        )
                    )
            if getVirtualmachines:
                for v in self.virtualmachines:
                    vms.append(
                        VMFolder.__cleanup(
                            "vm",
                            v.info(related=False)
                        )
                    )

            out = {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.name
            }
            if subFolders:
                out["subFolders"] = subFolders
            if vms:
                out["virtualmachines"] = vms

            return out

        except Exception as e:
            raise e






    # For a vCenter virtual machine folder get the plain list of the parent folders moIds.
    def parentList(self) -> list:
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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    # vCenter folders tree built using pvmomi.
    @staticmethod
    def folderTreeN(assetId) -> list:
        treeList = list()
        try:
            datacenters = Datacenter.oDatacenters(assetId)
            for dc in datacenters:
                parentFolderObj = dc.vmFolder
                moId = parentFolderObj._GetMoId()
                parentFolder = VMFolder(assetId, moId)
                subTree = parentFolder.info(getVirtualmachines=False)
                treeList.append(subTree)

            return treeList

        except Exception as e:
            raise e



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
                            "subFolders": {}
                        }
                    }
                    tree[folderObj._GetMoId()]["subFolders"].update(subTree)
                    VMFolder.__folderTree(child, subTree)

        return tree



    @staticmethod
    def __cleanup(oType: str, o: dict):
        if oType == "vm":
            if not o["networkDevices"]:
                del (o["networkDevices"])
            if not o["diskDevices"]:
                del (o["diskDevices"])
            del (o["numCpu"])
            del (o["numCoresPerSocket"])
            del (o["memoryMB"])
            del (o["version"])
        if oType == "folder":
             del (o["assetId"])
        if oType == "output":
            if not o["virtualmachines"]:
                del (o["virtualmachines"])

        return o
