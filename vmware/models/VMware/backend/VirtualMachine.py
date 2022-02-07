from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler



class VirtualMachine(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oVirtualMachine = self.__oVirtualMachineLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oDevices(self) -> list:
        try:
            config = self.oVirtualMachine.config
            return config.hardware.device
        except Exception as e:
            raise e



    def listVMNetworkInfo(self) -> list:
        nets = list()
        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    if hasattr(dev, 'backing'):
                        if hasattr(dev.backing, 'network'):  # Standard port group.
                            nets.append({
                                "label": dev.deviceInfo.label,
                                "network": str(dev.backing.network).strip("'").split(':')[1]
                            })
                        elif hasattr(dev.backing, 'port') and hasattr(dev.backing.port, 'portgroupKey'):  # Distributed port group.
                            nets.append({
                                "label": dev.deviceInfo.label,
                                "network": str(dev.backing.port.portgroupKey).strip("'").split(':')[1]
                            })
            return nets
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter virtual machine pyVmomi objects list.
    def oVirtualMachines(assetId) -> list:
        oVirtualMachineList = list()

        try:
            vmList = VmwareHandler(assetId).getObjects(vimType=vim.VirtualMachine)
            for v in vmList:
                oVirtualMachineList.append(v)

            return oVirtualMachineList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oVirtualMachineLoad(self):
        return self.getObjects(vimType=vim.VirtualMachine, moId=self.moId)[0]
