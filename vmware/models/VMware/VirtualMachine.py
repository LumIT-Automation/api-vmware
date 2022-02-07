from typing import List
from pyVmomi import vim

from vmware.models.VMware.VirtualMachineNetwork import VirtualMachineNetwork
from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class VirtualMachine(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVirtualMachine.name

        self.vmNetworks: List[VirtualMachineNetwork] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadVMNetworks(self) -> None:
        try:
            for l in self.listVMNetworkInfo():
                self.vmNetworks.append(
                    VirtualMachineNetwork(
                        self.assetId,
                        l["network"],
                        l["label"]
                    )
                )
        except Exception as e:
            raise e



    def info(self) -> dict:
        vmDisks = list()
        vmNets = list()

        try:
            config = self.oVirtualMachine.config
            self.loadVMNetworks()
            
            # Get network devices info.
            for net in self.vmNetworks:
                vmNets.append(
                    net.info()
                )

            # Get virtual disks info.
            # @todo: to VirtualMachineDisk class; use vim.vm.device.VirtualDisk.backing.datastore.
            for dev in config.hardware.device:
                if isinstance(dev, vim.vm.device.VirtualDisk):
                    vmDisks.append({
                        "label": dev.deviceInfo.label,
                        "size": str(dev.deviceInfo.summary)
                    })

            return {
                "name": config.name,
                "guestName": config.guestFullName,
                "version": config.version,
                "uuid": config.uuid,
                "numCpu": config.hardware.numCPU,
                "numCoresPerSocket": config.hardware.numCoresPerSocket,
                "memoryMB": config.hardware.memoryMB,
                "template": config.template,
                "networkDevices": vmNets,
                "diskDevices": vmDisks
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId, templatesAlso: bool = True) -> List[dict]:
        virtualmachines = list()

        try:
            for v in Backend.oVirtualMachines(assetId):
                if templatesAlso or not v.config.template:
                    data = VmwareHelper.vmwareObjToDict(v)
                    virtualmachines.append(data)

            return virtualmachines
        except Exception as e:
            raise e
