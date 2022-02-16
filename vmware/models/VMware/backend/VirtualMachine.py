from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


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



    def listVMDiskInfo(self) -> list:
        devs = list()

        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualDisk):
                    if hasattr(dev, 'backing') and hasattr(dev.backing, 'datastore'):
                        devs.append({
                            "datastore": str(dev.backing.datastore).strip("'").split(':')[1],
                            "label": dev.deviceInfo.label,
                            "size": str(dev.capacityInKB / 1024)+' MB'
                        })
            return devs
        except Exception as e:
            raise e



    def listVMNetworkInfo(self) -> list:
        nets = list()

        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    Log.log(dev, '_')
                    net = dict({
                        "label": dev.deviceInfo.label,
                        "deviceType": VirtualMachine.getEthernetDeviceType(dev)
                    })
                    if hasattr(dev, 'backing'):
                        try:
                            if hasattr(dev.backing, 'network'): # standard port group.
                                net.update({
                                    "network": str(dev.backing.network).strip("'").split(':')[1]
                                })
                            elif hasattr(dev.backing, 'port') and hasattr(dev.backing.port, 'portgroupKey'): # distributed port group.
                                net.update({
                                    "network": str(dev.backing.port.portgroupKey)
                                })
                        except Exception:
                            pass

                    nets.append(net)

            return nets
        except Exception as e:
            raise e





    def getVMDisk(self, diskLabel):
        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == diskLabel:
                    return dev
            raise CustomException(status=400, payload={"VMware": "Can't find the VM disk "+str(diskLabel)+"."})
        except Exception as e:
            raise e



    def getVMNic(self, nicLabel):
        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualEthernetCard) and dev.deviceInfo.label == nicLabel:
                    return dev
            raise CustomException(status=400, payload={"VMware": "Can't find the network card "+str(nicLabel)+"."})
        except Exception as e:
            raise e



    def buildDiskSpec(self, diskDevice: object, sizeMB: int, operation: str = 'edit'):
        try:
            diskSpec = vim.vm.device.VirtualDeviceSpec()
            diskSpec.device = diskDevice
            diskSpec.device.capacityInKB = int(sizeMB) * 1024
            diskSpec.device.capacityInBytes = int(sizeMB) * 1024 * 1024

            if operation == 'edit':
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            elif operation == 'add':
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            elif operation == 'remove':
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
            else:
                raise CustomException(status=400, payload={"VMware": "buildDiskSpec: not an operation."})

            return diskSpec
        except Exception as e:
            raise e



    def buildNicSpec(self, nicDevice: object, oNetwork: object, operation: str = 'edit'):
        try:
            nicSpec = vim.vm.device.VirtualDeviceSpec()
            nicSpec.device = nicDevice
            nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nicSpec.device.connectable.startConnected = True
            nicSpec.device.connectable.allowGuestControl = True
            nicSpec.device.connectable.connected = False

            if operation == 'edit':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            elif operation == 'add':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            elif operation == 'remove':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
            else:
                raise CustomException(status=400, payload={"VMware": "buildNicSpec: not an operation."})

            nicSpec.device.deviceInfo.summary = oNetwork.name
            nicSpec.device.backing.deviceName = oNetwork.name
            nicSpec.device.backing.network = oNetwork

            return nicSpec
        except Exception as e:
            raise e



    def buildNetworkSpec(self, networkDevicesData):
        from vmware.models.VMware.Network import Network
        specsList = list()
        devNum = 0 # Counter for the current (pre-deploy) network devices in the virtual machine template.

        """
        networkDevicesData example: [
            {
                "networkMoId": "network-1213",
                "label": "Network adapter 1",
                "deviceType": "vmxnet3"
            }
        ],
        """
        for devData in networkDevicesData:
            dev = None
            operations = list()
            netMoId = ''
            # Find the right device, or create a new one.
            if "label" in devData and devData["label"]:
                dev = self.getVMNic(devData["label"]) # This one raise for devic not found.
            else:
                # If a network label was not passed, get the first network device of the template and increment the counter.
                nicLabel = self.listVMNetworkInfo()[devNum]["label"]
                dev = self.getVMNic(nicLabel)
                devNum += 1

            if "networkMoId" in devData and devData["networkMoId"]:
                netMoId = devData["networkMoId"]

            # It's not possible to change the network device type. If it's not of the right type, remove and re-add it.
            if "deviceType" in devData and devData["deviceType"]:
                if devData["deviceType"] != VirtualMachine.getEthernetDeviceType(dev):
                    operations.append('remove')
                    operations.append('add')
                else:
                    operations.append('edit')

            if operations:
                for op in operations:
                    specsList.append( self.buildNicSpec(dev, Network(self.assetId, netMoId).oNetwork, op) )

        Log.log(specsList, '_')
        return specsList



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oVirtualMachines(assetId) -> list:
        try:
            return VmwareHandler(assetId).getObjects(vimType=vim.VirtualMachine)
        except Exception as e:
            raise e



    @staticmethod
    def getEthernetDeviceType(dev):
        if isinstance(dev, vim.vm.device.VirtualVmxnet3Vrdma):
            return 'vmrma'
        elif isinstance(dev, vim.vm.device.VirtualVmxnet3):
            return 'vmxnet3'
        elif isinstance(dev, vim.vm.device.VirtualE1000e):
            return 'e1000e'
        elif isinstance(dev, vim.vm.device.VirtualSriovEthernetCard):
            return 'sr-iov'
        elif isinstance(dev, vim.vm.device.VirtualE1000):
            return 'e1000'
        elif isinstance(dev, vim.vm.device.VirtualVmxnet2):
            return 'vmxnet2'
        elif isinstance(dev, vim.vm.device.VirtualVmxnet):
            return 'vmxnet'
        elif isinstance(dev, vim.vm.device.VirtualPCNet32):
            return 'pcnet32'
        else:
            return None



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oVirtualMachineLoad(self):
        try:
            return self.getObjects(vimType=vim.VirtualMachine, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
