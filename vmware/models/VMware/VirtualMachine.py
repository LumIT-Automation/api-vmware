from typing import List

from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper



class VirtualMachine(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVirtualMachine.name



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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId, related: bool = False) -> List[dict]:
        virtualmachines = list()

        try:
            for v in Backend.oVirtualMachines(assetId):
                data = VmwareHelper.vmwareObjToDict(v)
                virtualmachines.append(data)

            return virtualmachines
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
            vClient = VmwareHandler.connectToAssetAndGetContentStatic(assetId, silent)
            objList = vClient.getAllObjs([vim.VirtualMachine])
            return objList

        except Exception as e:
            raise e


