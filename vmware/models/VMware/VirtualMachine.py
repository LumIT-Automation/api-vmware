from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor
from vmware.helpers.Exception import CustomException
from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class VirtualMachine(VmwareContractor):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        info = {
            "diskDevices": [],
            "networkDevices": []
        }

        try:
            config = self.getVirtualMachineConfigObject()
            info.update({
                "name": config.name,
                "guestName": config.guestFullName,
                "version": config.version,
                "uuid": config.uuid,
                "numCpu": config.hardware.numCPU,
                "numCoresPerSocket": config.hardware.numCoresPerSocket,
                "memoryMB": config.hardware.memoryMB,
                "template": config.template
            })

            for dev in config.hardware.device:
                if isinstance(dev, vim.vm.device.VirtualDisk):
                    info["diskDevices"].append({
                        "label": dev.deviceInfo.label,
                        "size": str(dev.deviceInfo.summary)
                    })

                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    if hasattr(dev, 'backing'):
                        if hasattr(dev.backing, 'network'): # Standard port group.
                            info["networkDevices"].append({
                                "label": dev.deviceInfo.label,
                                "network": str(dev.backing.network)
                            })
                        elif hasattr(dev.backing, 'port') and hasattr(dev.backing.port, 'portgroupKey'): # Distributed port group.
                            info["networkDevices"].append({
                                "label": dev.deviceInfo.label,
                                "network": str(dev.backing.port.portgroupKey)
                            })

            return info

        except Exception as e:
            raise e



    def getVirtualMachineConfigObject(self) -> object:
        try:
            self.getVMwareObject()
            if not hasattr(self.oCluster, 'config'):
                raise CustomException(status=400, payload={"VMware: this object is not a virtual machine."})

            return self.oCluster.config

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        try:
            self._getContainer(vim.VirtualMachine)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = True) -> dict:
        vmList = []
        try:
            vmObjList = VirtualMachine.listVirtualMachinesOnlyObjects(assetId, silent)

            for vm in vmObjList:
                vmList.append(VmwareHelper.vmwareObjToDict(vm))

            return dict({
                "items": vmList
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter virtual machines (not templates) pyVmomi objects list.
    def listVirtualMachinesOnlyObjects(assetId, silent: bool = True) -> list:
        vmObjList = list()
        try:
            objList = VirtualMachine.listVirtualMachinesObjects(assetId, silent)
            for obj in objList:
                if not obj.config.template:
                    vmObjList.append(obj)

            return vmObjList

        except Exception as e:
            raise e



    @staticmethod
    # vCenter virtual machines and templates pyVmomi objects list.
    def listVirtualMachinesObjects(assetId, silent: bool = True) -> list:
        objList = list()
        try:
            vClient = VmwareContractor.connectToAssetAndGetContentStatic(assetId, silent)
            objList = vClient.getAllObjs([vim.VirtualMachine])
            return objList

        except Exception as e:
            raise e


