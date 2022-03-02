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
                            if dev.backing.eagerlyScrub:
                                devType = 'thick eager zeroed'
                            else:
                                devType = 'thick lazy zeroed'
                        devs.append({
                            "datastore": str(dev.backing.datastore).strip("'").split(':')[1],
                            "label": dev.deviceInfo.label,
                            "sizeMB": (dev.capacityInKB / 1024),
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

                backingSpec = diskSpec.device.backing
                diskSpec.device.backing = self._buildDiskBackingSpec(
                    spec=backingSpec,
                    oDatastore=data["datastore"].oDatastore,
                    deviceType=data["deviceType"],
                    filePath=data["filePath"]
                )

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
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1024
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1024 * 1024
                diskSpec.device.controllerKey = controller.key
                diskSpec.device.unitNumber = unitNumber
                diskSpec.device.deviceInfo = vim.Description()
                if "deviceLabel" in data:
                    diskSpec.device.deviceInfo.label = data["deviceLabel"]

                diskSpec.device.backing = self._buildDiskBackingSpec(
                    spec=None,
                    oDatastore=data["datastore"].oDatastore,
                    deviceType=data["deviceType"],
                    filePath=data["filePath"]
                )

            elif data["operation"] == 'remove':
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                diskSpec.device = data["device"]
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
                    nicSpec.device.deviceInfo = vim.Description()
                    nicSpec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicSpec.device.connectable.startConnected = True
                    nicSpec.device.connectable.allowGuestControl = True
                    nicSpec.device.connectable.connected = False
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                if "deviceLabel" in data:
                    nicSpec.device.deviceInfo.label = data["deviceLabel"]
                nicSpec.device.backing.deviceName = data["network"].oNetwork.name
                nicSpec.device.backing.network = data["network"].oNetwork
            elif data["operation"] == 'add':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                nicSpec.device = VirtualMachine.getEthernetDeviceInstance(data["deviceType"])
                nicSpec.device.deviceInfo = vim.Description()
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                if "deviceLabel" in data:
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
    def buildExistentNetDevicesSpecs(self, templDevData: list) -> list:
        from vmware.models.VMware.Network import Network
        templDevsInfo = self.listVMNetworkInfo()  # The network info of the template.
        devsSpecsData = list() # Intermediate data structure.
        specsList = list() # Real spec data obtained from  self.buildNicSpec.

        try:
            for devData in templDevData:
                # Use label to find the right device.
                if "label" in devData and devData["label"]:
                    found = False
                    # Make a copy of the list to safely remove items from the same list that we are looping.
                    for devInfo in list(templDevsInfo):
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

                            # If there is a match, remove the element from the list.
                            templDevsInfo.remove(devInfo)
                            break

                    # Device not found: error in input data.
                    if not found:
                        raise CustomException(status=400, payload={"VMware": "buildExistentNetDevicesSpecs: Can't find the network card: \"" + str(devData["label"]) + "\"."})

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



    # This one build the spec data structure for the devices present in the template.
    def buildExistentDiskDevicesSpecs(self, templDevData: list) -> list:
        from vmware.models.VMware.Datastore import Datastore
        templDevsInfo = self.listVMDiskInfo()  # The disk info of the template.
        devsSpecsData = list() # Intermediate data structure.
        specsList = list() # Real spec data obtained from  self.buildNicSpec.

        try:
            for devData in templDevData:
                # Use label to find the right device.
                if "label" in devData and devData["label"]:
                    found = False
                    # Make a copy of the list to safely remove items from the same list that we are looping.
                    for devInfo in list(templDevsInfo):
                        if devInfo["label"] == devData["label"]:
                            found = True
                            device = self.getVMDisk(devInfo["label"])
                            datastore = Datastore(self.assetId, devData["datastoreMoId"])
                            filePath = ""
                            # If the disk is moving in another datastore, the datastore name in the filePath is also needed.
                            if devData["datastoreMoId"] != device.backing.datastore._GetMoId():
                                filePath = datastore.info()["name"]
                            devsSpecsData.append({
                                "operation": "edit",
                                "device": self.getVMDisk(devInfo["label"]),
                                "deviceLabel": devData["label"],
                                "deviceType": devData["deviceType"],
                                "sizeMB": devData["sizeMB"],
                                "datastore": datastore,
                                "filePath": filePath
                            })

                            # If there is a match, remove the element from the list.
                            templDevsInfo.remove(devInfo)
                            break

                    # Device not found: error in input data.
                    if not found:
                        raise CustomException(status=400, payload={"VMware": "buildExistentDiskDevicesSpecs: Can't find the disk: \"" + str(devData["label"]) + "\"."})

            # If there are some template devices without match in the input data, they should be removed.
            if templDevsInfo:
                for devInfo in templDevsInfo:
                    devsSpecsData.append({
                        "operation": "remove",
                        "device": self.getVMDisk(devInfo["label"])
                    })

            for data in devsSpecsData:
                specsList.append(self.buildDiskSpec(data))

            return specsList
        except Exception as e:
            raise e


    # This one build the spec data structure for the devices not present in the template.
    def buildNewDiskDevicesSpecs(self, newDevData: list, vmDatastoreMoId: str) -> list:
        from vmware.models.VMware.Datastore import Datastore
        devsSpecsData = list() # Intermediate data structure.
        specsList = list() # Real spec data obtained from  self.buildNicSpec.

        try:
            # Build an intermediate data structure and pass it to self.buildNicSpec to obtain the real spec data struct.
            for devData in newDevData:
                dsStore = Datastore(self.assetId, devData["datastoreMoId"])
                # If the disk is not in the default datastore of the VM, the datastore name in the filePath is also needed.
                filePath = ""
                if devData["datastoreMoId"] != vmDatastoreMoId:
                    filePath = dsStore.info()["name"]
                devsSpecsData.append({
                    "operation": "add",
                    "device": None,
                    "deviceLabel": devData["label"],
                    "deviceType": devData["deviceType"],
                    "sizeMB": devData["sizeMB"],
                    "datastore": dsStore,
                    "filePath": filePath
                })

            for data in devsSpecsData:
                specsList.append(self.buildDiskSpec(data))

            return specsList
        except Exception as e:
            raise e



    def buildNetworkSpec(self, devicesData: dict) -> list:
        specsList = list()
        """
        devicesData (passed via POST) example:
        {
            "existent": [
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
        How to use it:
        "templateDefault" are the nics in the template. To remove them, pass an empty list.
        To leave them untouched, remove completely the "templateDefault" dict field.
        "new" are the supplementary nics added to the new vm. 
        """
        try:
            if "existent" in devicesData:
                specsList.extend(self.buildExistentNetDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                specsList.extend(self.buildNewNetDevicesSpecs(devicesData["new"]))
            return specsList
        except Exception as e:
            raise e



    def buildStorageSpec(self, devicesData: dict, vmDatastoreMoId: str) -> list:
        specsList = list()
        """
        devicesData (passed via POST) example:
        {
            "existent": [
                {
                    "datastoreMoId": "datastore-2341",
                    "label": "Hard disk 1",
                    "sizeMB": 2048,
                    "deviceType": "thin"
                }
            ],
            "new": [
                ...
            ]
        }
        How to use it:
        "templateDefault" are the disks in the template. To remove them, pass an empty list.
        To leave them untouched, remove completely the "templateDefault" dict field.
        "new" are the supplementary disks added to the new vm. 
        """
        try:
            if "existent" in devicesData:
                specsList.extend(self.buildExistentDiskDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                specsList.extend(self.buildNewDiskDevicesSpecs(devicesData["new"], vmDatastoreMoId))

            return specsList
        except Exception as e:
            raise e



    def buildVMCloneSpecs(self, oDatastore: object, oCluster: object, data: dict, devsSpecs: object = None, oCustomSpec: object = None):
        try:
            cloneSpec = vim.vm.CloneSpec()  # virtual machine specifications for a clone operation.

            # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
            relocateSpec = vim.vm.RelocateSpec()
            relocateSpec.datastore = oDatastore
            relocateSpec.pool = oCluster.resourcePool  # The resource pool associated to this cluster.

            cloneSpec.location = relocateSpec
            if "powerOn" in data:
                cloneSpec.powerOn = data["powerOn"]
                data.pop("powerOn")

            cloneSpec.config = self.buildVMConfigSpecs(data, devsSpecs)

            # Apply the guest OS customization specifications.
            if oCustomSpec:
                cloneSpec.customization = oCustomSpec.spec

            return cloneSpec

        except Exception as e:
            raise e



    def buildVMConfigSpecs(self, data: dict, devsSpecs: object = None):
        try:
            configSpec = vim.vm.ConfigSpec()

            if "numCpu" in data and data["numCpu"]:
                configSpec.numCPUs = data["numCpu"]
            if "numCoresPerSocket" in data and data["numCoresPerSocket"]:
                configSpec.numCoresPerSocket = data["numCoresPerSocket"]
            if "memoryMB" in data and data["memoryMB"]:
                configSpec.memoryMB = data["memoryMB"]
            if "notes" in data and data["notes"]:
                configSpec.annotation = data["notes"]

            if devsSpecs:
                configSpec.deviceChange = devsSpecs

            return configSpec
        except Exception as e:
            raise e



    def clone(self, oVMFolder: object, vmName: str, cloneSpec: object) -> str:
        try:
            task = self.oVirtualMachine.Clone(folder=oVMFolder, name=vmName, spec=cloneSpec)
            return task._GetMoId()
        except Exception as e:
            raise e



    def reconfig(self, configSpec: object) -> str:
        try:
            task = self.oVirtualMachine.ReconfigVM_Task(spec=configSpec)
            return task._GetMoId()
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



    def _buildDiskBackingSpec(self, spec: object, oDatastore: object, deviceType: str, filePath: str):
        try:
            if not spec:
                spec = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                spec.diskMode = 'persistent'

            spec.datastore = oDatastore
            if deviceType == 'thin':
                spec.thinProvisioned = True
            elif deviceType == 'thick lazy zeroed':
                spec.thinProvisioned = False
                spec.eagerlyScrub = False
            elif deviceType == 'thick eager zeroed':
                spec.thinProvisioned = False
                spec.eagerlyScrub = True

            if filePath:
                spec.fileName = '[' + str(filePath) + ']'

            return spec
        except Exception as e:
            raise e
