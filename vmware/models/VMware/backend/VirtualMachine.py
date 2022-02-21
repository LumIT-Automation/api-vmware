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
                        if dev.backing.thinProvisioned:
                            devType = 'thin'
                        else:
                            devType = 'thick'
                        devs.append({
                            "datastore": str(dev.backing.datastore).strip("'").split(':')[1],
                            "label": dev.deviceInfo.label,
                            "size": str(dev.capacityInKB / 1024)+' MB',
                            "deviceType": devType
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



    def buildDiskSpec(self, data: dict) -> object:
        try:
            diskSpec = vim.vm.device.VirtualDeviceSpec()
            if data["operation"] == "edit":
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                diskSpec.device = data["device"]
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1024
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1024 * 1024
                if data["deviceType"] == 'thin':
                    diskSpec.device.backing.thinProvisioned = True
            elif data["operation"] == 'add':
                    # Get the controller device.
                    controller = None
                    for dev in self.oDevices():
                        if isinstance(dev, vim.vm.device.VirtualSCSIController):
                            controller = dev
                    if not controller:
                        raise CustomException(status=400, payload={"VMware": "add disk operation: controller not found!"})

                    # Set the disk unit number.
                    unitNumber = 0
                    for dev in self.oDevices():
                        if hasattr(dev.backing, 'fileName'):
                            if int(dev.unitNumber) + 1 > unitNumber:
                                unitNumber = int(dev.unitNumber) + 1
                            if unitNumber == 7: # unit number 7 is reserved for scsi controller.
                                unitNumber += 1
                            if unitNumber >= 16:
                                raise CustomException(status=400, payload={"VMware": "add disk operation: too many virtual disks!"})

                    diskSpec.fileOperation = "create"
                    diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                    diskSpec.device = vim.vm.device.VirtualDisk()
                    diskSpec.device.controllerKey = controller.key
                    diskSpec.device.deviceInfo = vim.Description()
                    diskSpec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                    diskSpec.device.backing.diskMode = 'persistent'
                    diskSpec.device.backing.datastore = data["datastore"].oDatastore
                    diskSpec.device.unitNumber = unitNumber
                    if data["deviceType"] == 'thin':
                        diskSpec.device.backing.thinProvisioned = True
                    diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1024
                    diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1024 * 1024
            elif data["operation"] == 'remove':
                    diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                    diskSpec.device = data["device"]
            else:
                raise CustomException(status=400, payload={"VMware": "buildDiskSpec: not an operation."})

            return diskSpec
        except Exception as e:
            raise e



    def buildStorageSpec(self, devicesData: dict) -> list:
        from vmware.models.VMware.Datastore import Datastore
        specsList = list()
        tDevsInfo = self.listVMDiskInfo() # The storage info of the template.
        allDevsSpecsData = list() # The data/devices needed to build the disks specs.

        """
        diskDevices (passed via POST) example:
        [
            {
                "datastoreMoId": "datastore-2341",
                "Label": "Hard disk 1",
                "sizeMB": 1024,
                "deviceType": "thin"
            },
        [
        """

        try:
            for devData in devicesData:
                # Find the right device, or get the first one found.
                if "label" in devData and devData["label"]:
                    for devInfo in tDevsInfo:
                        if devInfo["label"] == devData["label"]:
                            if devInfo["deviceType"] == devData["deviceType"]:
                                allDevsSpecsData.append({
                                    "operation": "edit",
                                    "device": self.getVMDisk(devInfo["label"]),
                                    "deviceLabel": devInfo["label"],
                                    "deviceType": devData["deviceType"],
                                    "sizeMB": devData["sizeMB"],
                                    "datastore": Datastore(self.assetId, devData["datastoreMoId"])
                                })
                            else:
                                # If the wanted device is different from the one in the template it's not possible
                                # to change it, so remove it and add a new one.
                                allDevsSpecsData.extend([
                                    {
                                        "operation": "remove",
                                        "device": self.getVMDisk(devInfo["label"]),
                                    },
                                    {
                                        "operation": "add",
                                        "device": None,
                                        "deviceLabel": devInfo["label"],
                                        "deviceType": devData["deviceType"],
                                        "sizeMB": devData["sizeMB"],
                                        "datastore": Datastore(self.assetId, devData["datastoreMoId"])
                                    }
                                ])

                            # If there is a match, subtract the element from both the lists.
                            tDevsInfo.remove(devInfo)
                            devicesData.remove(devData)
                            break
                    # A passed (label) device must have a match. If not, raise an exception.
                    # To ask for new device leave blank the label field in diskDevicesData
                    if not allDevsSpecsData or allDevsSpecsData[-1]["deviceLabel"] != devData["label"]:
                        raise CustomException(status=400, payload={
                            "VMware": "buildStorageSpec: Can't find the disk: \"" + str(devData["label"]) + "\"."})

            # Check the length of the lists.
            # If len(devData) == len(tDevsInfo) -> all disks matches, go forward.
            # If len(devData) > len(tDevsInfo) -> some disks are missing in the template. Add them.
            # if len(devData) < len(tDevsInfo) -> some disks in the template are not needed. Remove them.

            # Check if there are still some passed devices to assign to the new virtual machine.
            if devicesData:
                for devData in devicesData:
                    # If there are still some unassigned devices in the template pick the first one.
                    if tDevsInfo:
                        devInfo = tDevsInfo[0]
                        allDevsSpecsData.append({
                            "operation": "edit",
                            "device": self.getVMDisk(devInfo["label"]),
                            "deviceLabel": devInfo["label"],
                            "deviceType": devData["deviceType"],
                            "sizeMB": devData["sizeMB"],
                            "datastore": Datastore(self.assetId, devData["datastoreMoId"])
                        })
                        tDevsInfo.remove(devInfo)
                    # Otherwise a new nic will be added.
                    else:
                        allDevsSpecsData.append({
                            "operation": "add",
                            "device": None,
                            "deviceLabel": "",
                            "deviceType": devData["deviceType"],
                            "sizeMB": devData["sizeMB"],
                            "datastore": Datastore(self.assetId, devData["datastoreMoId"])
                        })
            # If there are still some unassigned devices in the template but the passed devs are all assigned,
            # this mean that the remaining devices should be removed from the template.
            else:
                if tDevsInfo:
                    for devInfo in tDevsInfo:
                        allDevsSpecsData.append({
                            "operation": "remove",
                            "device": self.getVMDisk(devInfo["label"])
                        })
                        tDevsInfo.remove(devInfo)

            # Build all the specs cycling through the allDevsSpecsData list.
            for data in allDevsSpecsData:
                specsList.append(self.buildDiskSpec(data))

            return specsList
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
                    nicSpec.device.deviceInfo = vim.Description()
                    nicSpec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicSpec.device.connectable.startConnected = True
                    nicSpec.device.connectable.allowGuestControl = True
                    nicSpec.device.connectable.connected = False
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                nicSpec.device.deviceInfo.label = data["deviceLabel"]
                nicSpec.device.backing.deviceName = data["network"].oNetwork.name
                nicSpec.device.backing.network = data["network"].oNetwork
            elif data["operation"] == 'add':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                nicSpec.device = VirtualMachine.getEthernetDeviceInstance(data["deviceType"])
                nicSpec.device.deviceInfo = vim.Description()
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                nicSpec.device.deviceInfo.label = data["deviceLabel"]
                nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                nicSpec.device.connectable.startConnected = True
                nicSpec.device.connectable.allowGuestControl = True
                nicSpec.device.connectable.connected = False
                nicSpec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                nicSpec.device.backing.deviceName = data["network"].oNetwork.name
                nicSpec.device.backing.network = data["network"].oNetwork
                if "additionalData" in data:
                    nicSpec.device.controllerKey = data["additionalData"]["controllerKey"]
                    nicSpec.device.unitNumber = data["additionalData"]["unitNumber"]

            elif data["operation"] == 'remove':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                nicSpec.device = data["device"]
            else:
                raise CustomException(status=400, payload={"VMware": "buildNicSpec: not an operation."})

            return nicSpec
        except Exception as e:
            raise e



    # This one build the spec data structure for the devices present in the template.
    def buildTemplateNetDevicesSpecs(self, templDevData: list) -> list:
        from vmware.models.VMware.Network import Network
        templDevsInfo = self.listVMNetworkInfo()  # The network info of the template.
        devsSpecsData = list() # Intermediate data structure.
        specsList = list() # Real spec data obtained from  self.buildNicSpec.

        try:
            for devData in templDevData:
                # Use label to find the right device.
                if "label" in devData and devData["label"]:
                    found = False
                    for devInfo in templDevsInfo:
                        if devInfo["label"] == devData["label"]:
                            found = True
                            if devInfo["deviceType"] == devData["deviceType"]: # Both the label and deviceType matches: device found ok.
                                devsSpecsData.append({
                                    "operation": "edit",
                                    "device": self.getVMNic(devInfo["label"]),
                                    "deviceLabel": devData["label"],
                                    "deviceType": devData["deviceType"],
                                    "network": Network(self.assetId, devData["networkMoId"])
                                })
                            else:
                                # The label matches but the device type is wrong. Cannot change it, so remove it and add a new one.
                                oldDev = self.getVMNic(devInfo["label"])
                                # Put the re-added nic in the same pci slot to avoid changing the nics order.
                                devAdditionalData = dict({
                                    "controllerKey": "",
                                    "unitNumber": ""
                                })
                                devAdditionalData["controllerKey"] = oldDev.controllerKey
                                devAdditionalData["unitNumber"] = oldDev.unitNumber
                                devsSpecsData.extend([
                                    {
                                        "operation": "remove",
                                        "device": oldDev
                                    },
                                    {
                                        "operation": "add",
                                        "device": None,
                                        "deviceLabel": devData["label"],
                                        "deviceType": devData["deviceType"],
                                        "network": Network(self.assetId, devData["networkMoId"]),
                                        "devAdditionalData": devAdditionalData
                                    }
                                ])

                            # If there is a match, subtract the element from both the lists.
                            templDevsInfo.remove(devInfo)
                            break

                    # Device not found: error in input data.
                    if not found:
                        raise CustomException(status=400, payload={"VMware": "buildTemplateNetDevicesSpecs: Can't find the network card: \"" + str(devData["label"]) + "\"."})

            # If there are some template devices without match in the input data, they should be removed.
            if templDevsInfo:
                for devInfo in templDevsInfo:
                    devsSpecsData.append({
                        "operation": "remove",
                        "device": self.getVMNic(devInfo["label"])
                    })

            for data in devsSpecsData:
                specsList.append(self.buildNicSpec(data))

            return specsList
        except Exception as e:
            raise e



    # This one build the spec data structure for the devices not present in the template.
    def buildNewNetDevicesSpecs(self, newDevData: list) -> list:
        from vmware.models.VMware.Network import Network
        devsSpecsData = list() # Intermediate data structure.
        specsList = list() # Real spec data obtained from  self.buildNicSpec.

        try:
            # Build an intermediate data structure and pass it to self.buildNicSpec to obtain the real spec data struct.
            for devData in newDevData:
                devsSpecsData.append({
                    "operation": "add",
                    "device": None,
                    "deviceLabel": devData["label"],
                    "deviceType": devData["deviceType"],
                    "network": Network(self.assetId, devData["networkMoId"])
                })

            for data in devsSpecsData:
                specsList.append(self.buildNicSpec(data))

            return specsList
        except Exception as e:
            raise e



    def buildNetworkSpec(self, devicesData: dict) -> list:
        specsList = list()
        """
        devicesData (passed via POST) example:
        {
            "templateDefault": [
                {
                    "networkMoId": "network-1213",
                    "label": "Network adapter 1",
                    "deviceType": "vmxnet3"
                }
            ],
            "new": [
                ...
            ]
        }
        """
        try:
            if "templateDefault" in devicesData:
                specsList.extend(self.buildTemplateNetDevicesSpecs(devicesData["templateDefault"]))
            if "new" in devicesData:
                specsList.extend(self.buildNewNetDevicesSpecs(devicesData["new"]))
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
