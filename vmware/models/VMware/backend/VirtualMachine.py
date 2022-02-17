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
            raise CustomException(status=400, payload={"VMware": "Can't find the network card: \""+str(nicLabel)+"\"."})
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



    def buildNicSpec(self, data: dict) -> object:
        try:
            nicSpec = vim.vm.device.VirtualDeviceSpec()
            if data["operation"] == "edit":
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                if VirtualMachine.getEthernetDeviceType(data["device"]) == data["deviceType"]:
                    nicSpec.device = data["device"]
                else:
                    nicSpec.device = VirtualMachine.getEthernetDeviceInstance(data["deviceType"])
                    nicSpec.device.key = 4115
                    nicSpec.device.deviceInfo = vim.Description()
                    nicSpec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicSpec.device.connectable.startConnected = True
                    nicSpec.device.connectable.allowGuestControl = True
                    nicSpec.device.connectable.connected = False
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                nicSpec.device.backing.deviceName = data["network"].oNetwork.name
                nicSpec.device.backing.network = data["network"].oNetwork
            elif data["operation"] == 'add':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                nicSpec.device = vim.vm.device.VirtualE1000e()
                nicSpec.device.key = 4113
                nicSpec.device.deviceInfo = vim.Description()
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                nicSpec.device.connectable.startConnected = True
                nicSpec.device.connectable.allowGuestControl = True
                nicSpec.device.connectable.connected = False
                nicSpec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                nicSpec.device.backing.deviceName = data["network"].oNetwork.name
                nicSpec.device.backing.network = data["network"].oNetwork
            elif data["operation"] == 'remove':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                nicSpec.device = data["device"]
            else:
                raise CustomException(status=400, payload={"VMware": "buildNicSpec: not an operation."})

            return nicSpec
        except Exception as e:
            raise e



    def buildNetworkSpec(self, networkDevicesData: list) -> list:
        from vmware.models.VMware.Network import Network
        specsList = list()
        tDevsInfo = self.listVMNetworkInfo() # The network info of the template.
        allDevsSpecsData = list() # The data/devices needed to build the nic specs.

        """
        networkDevicesData (passed via POST) example: 
        [
            {
                "networkMoId": "network-1213",
                "label": "Network adapter 1",
                "deviceType": "vmxnet3"
            }
        ],
        """

        try:
            for devData in networkDevicesData:
                # Find the right device, or get the first one found.
                if "label" in devData and devData["label"]:
                    for nicInfo in tDevsInfo:
                        if nicInfo["label"] == devData["label"]:
                            if nicInfo["deviceType"] == devData["deviceType"]:
                                allDevsSpecsData.append({
                                    "operation":  "edit",
                                    "device": self.getVMNic(nicInfo["label"]),
                                    "deviceLabel": nicInfo["label"],
                                    "deviceType": devData["deviceType"],
                                    "network": Network(self.assetId, devData["networkMoId"])
                                })
                            else:
                                # If the wanted nic is an adapter different from the one in the template it's not possible
                                # to change it, so remove it and add a new one.
                                allDevsSpecsData.extend([
                                    {
                                        "operation": "remove",
                                        "device": self.getVMNic(nicInfo["label"]),
                                    },
                                    {
                                        "operation": "add",
                                        "device": None,
                                        "deviceLabel": nicInfo["label"],
                                        "deviceType": devData["deviceType"],
                                        "network": Network(self.assetId, devData["networkMoId"])
                                    }
                                ])

                            # If there is a match, subtract the element from both the lists.
                            tDevsInfo.remove(nicInfo)
                            networkDevicesData.remove(devData)
                            break
                    if not allDevsSpecsData[-1]["deviceLabel"] == devData["label"]:
                        # A passed network card must have a match. Otherwise, leave blank the label in networkDevicesData.
                        raise CustomException(status=400, payload={"VMware": "buildNetworkSpec: Can't find the network card: \""+str(nicLabel)+"\"."})

            # Check the length of the lists.
            # If len(devData) == len(tDevsInfo) -> all nics matches, go forward.
            # If len(devData) > len(tDevsInfo) -> some cards are missing in the template. Add them.
            # if len(devData) < len(tDevsInfo) -> some card in the template are not needed. Remove them.

            # Check if there are still some passed network cards to assign to the new virtual machine.
            if networkDevicesData:
                for devData in networkDevicesData:
                    # If there are still some unassigned network cards in the template pick the first one.
                    if tDevsInfo:
                        nicInfo = tDevsInfo[0]
                        allDevsSpecsData.append({
                            "operation": "edit",
                            "device": self.getVMNic(nicInfo["label"]),
                            "deviceLabel": nicInfo["label"],
                            "deviceType": devData["deviceType"],
                            "network": Network(self.assetId, devData["networkMoId"])
                        })
                        tDevsInfo.remove(nicInfo)
                        networkDevicesData.remove(devData)
                    # Otherwise a new nic will be added.
                    else:
                        allDevsSpecsData.append({
                            "operation": "add",
                            "device": None,
                            "deviceLabel": "",
                            "deviceType": devData["deviceType"],
                            "network": Network(self.assetId, devData["networkMoId"])
                        })
                        networkDevicesData.remove(devData)
            # If there are still some unassigned network cards in the template but the passed nics are all assigned,
            # this mean that the remaining nics should be removed from the template.
            else:
                if tDevsInfo:
                    for nicInfo in tDevsInfo:
                        allDevsSpecsData.append({
                            "operation": "remove",
                            "device": self.getVMNic(nicInfo["label"])
                        })
                        tDevsInfo.remove(nicInfo)

            # Build all the specs cycling through the allDevsSpecsData list.
            for data in allDevsSpecsData:
                specsList.append( self.buildNicSpec(data) )

            Log.log(specsList, 'SSSSSSSSSSSSSSSSSSSSSSSSSSs')
            return specsList
        except Exception as e:
            raise e



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
    def getEthernetDeviceType(dev: object):
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



    @staticmethod
    def getEthernetDeviceInstance(devString: str) -> object:
        if devString == 'vmrma':
            return vim.vm.device.VirtualVmxnet3Vrdma()
        elif devString == 'vmxnet3':
            return vim.vm.device.VirtualVmxnet3()
        elif devString == 'e1000e':
            return vim.vm.device.VirtualE1000e()
        elif devString == 'sr-iov':
            return vim.vm.device.VirtualSriovEthernetCard()
        elif devString == 'e1000':
            return vim.vm.device.VirtualE1000()
        elif devString == 'vmxnet2':
            return vim.vm.device.VirtualVmxnet2()
        elif devString == 'vmxnet':
            return vim.vm.device.VirtualVmxnet()
        elif devString == 'pcnet32':
            return vim.vm.device.VirtualPCNet32()
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
