from typing import List
from pyVmomi import vim

from vmware.models.VMware.VirtualMachineNetwork import VirtualMachineNetwork
from vmware.models.VMware.VirtualMachineDatastore import VirtualMachineDatastore
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
        self.vmDatastores: List[VirtualMachineDatastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadVMDatastores(self) -> None:
        try:
            for l in self.listVMDiskInfo():
                self.vmDatastores.append(
                    VirtualMachineDatastore(
                        self.assetId,
                        l["datastore"],
                        l["label"],
                        l["size"]
                    )
                )
        except Exception as e:
            raise e



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
            self.loadVMDatastores()
            self.loadVMNetworks()

            # Get network devices info.
            for net in self.vmNetworks:
                vmNets.append(
                    net.info()
                )

            # Get virtual disks info.
            for disk in self.vmDatastores:
                vmDisks.append(
                    disk.info()
                )

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
