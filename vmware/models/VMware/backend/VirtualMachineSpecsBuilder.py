from pyVmomi import vim

from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VirtualMachineSpecsBuilder(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.diskLocators = []
        self.relocateSpec = vim.vm.RelocateSpec() # where put the new virtual machine.
        self.configSpec = vim.vm.ConfigSpec() # virtual machine configuration specification.
        self.cloneSpec = None # virtual machine specifications for a clone operation.
        self.storageSpec = list()
        self.networkSpec = list()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def buildNetworkSpec(self, devicesData: dict) -> None:
        """
        devicesData example:
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

        "existent" are the nics in the template.
            To remove them, pass an empty list.
            To leave them untouched, remove completely the "existent" dict field.

        "new" are the supplementary nics added to the new vm.
        """

        try:
            if "existent" in devicesData:
                self.networkSpec.extend(self.__buildExistentNetDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                self.networkSpec.extend(self.__buildNewNetDevicesSpecs(devicesData["new"]))
        except Exception as e:
            raise e



    def buildStorageSpec(self, devicesData: dict, vmDatastoreMoId: list) -> None:
        """
        devicesData example:
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

        "existent" are the disks in the template.
            To remove them, pass an empty list.
            To leave them untouched, remove completely the "existent" dict field.

        "new" are the supplementary disks added to the new vm.
        """

        try:
            if "existent" in devicesData:
                self.storageSpec.extend(self.__buildExistentDiskDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                self.storageSpec.extend(self.__buildNewDiskDevicesSpecs(devicesData["new"], vmDatastoreMoId))
        except Exception as e:
            raise e



    def buildVMCloneSpecs(self, oDatastore: object, data: dict, cluster: object = None, host: object = None, devsSpecs: object = None, oCustomSpec: object = None):
        try:
            self.cloneSpec = vim.vm.CloneSpec()
            self.relocateSpec.datastore = oDatastore
            if cluster:
                self.relocateSpec.pool = cluster.oCluster.resourcePool # The resource pool associated to this cluster.
                if host:
                    self.relocateSpec.host = host.oHostSystem
            elif host:
                self.relocateSpec.pool = host.oHostSystem.parent.resourcePool # Standalone host resource pool.
                self.relocateSpec.host = host.oHostSystem
            else:
                raise CustomException(status=400, payload={"VMware": "Missing cluster or host params."})

            self.relocateSpec.disk = self.diskLocators
            self.cloneSpec.location = self.relocateSpec
            if "powerOn" in data:
                self.cloneSpec.powerOn = data["powerOn"]
                data.pop("powerOn")

            self.buildVMConfigSpecs(data, devsSpecs)
            self.cloneSpec.config = self.configSpec

            # Apply the guest OS customization specifications.
            if oCustomSpec:
                self.cloneSpec.customization = oCustomSpec.spec
        except Exception as e:
            raise e



    def buildVMConfigSpecs(self, data: dict, devsSpecs: object = None) -> None:
        try:
            if "numCpu" in data and data["numCpu"]:
                self.configSpec.numCPUs = data["numCpu"]
            if "numCoresPerSocket" in data and data["numCoresPerSocket"]:
                self.configSpec.numCoresPerSocket = data["numCoresPerSocket"]
            if "memoryMB" in data and data["memoryMB"]:
                self.configSpec.memoryMB = data["memoryMB"]
            if "notes" in data and data["notes"]:
                self.configSpec.annotation = data["notes"]

            if devsSpecs:
                self.configSpec.deviceChange = devsSpecs
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __buildDiskSpec(self, data: dict) -> object:
        try:
            diskSpec = vim.vm.device.VirtualDeviceSpec()
            if data["operation"] == "edit":
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                diskSpec.device = data["device"]
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1024 # MiB.
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1024 * 1024

                backingSpec = diskSpec.device.backing
                diskSpec.device.backing = self.__buildDiskBackingSpec(
                    spec=backingSpec,
                    oDatastore=data["datastore"].oDatastore,
                    deviceType=data["deviceType"],
                    filePath=data["filePath"]
                )

                if data["deviceKey"]:
                    diskLocator = vim.vm.RelocateSpec.DiskLocator()
                    diskLocator.diskId = data["deviceKey"]
                    diskLocator.datastore = data["datastore"].oDatastore
                    diskLocator.diskBackingInfo = diskSpec.device.backing

                    self.diskLocators.append(diskLocator)

            elif data["operation"] == 'add':
                diskSpec.fileOperation = "create"
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                diskSpec.device = vim.vm.device.VirtualDisk()
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1024
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1024 * 1024
                diskSpec.device.controllerKey = data["controllerKey"]
                diskSpec.device.unitNumber = data["newDiskNumber"]
                diskSpec.device.deviceInfo = vim.Description()
                if "deviceLabel" in data:
                    diskSpec.device.deviceInfo.label = data["deviceLabel"]

                diskSpec.device.backing = self.__buildDiskBackingSpec(
                    spec=None,
                    oDatastore=data["datastore"].oDatastore,
                    deviceType=data["deviceType"],
                    filePath=data["filePath"]
                )

            elif data["operation"] == 'remove':
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                diskSpec.device = data["device"]
            else:
                raise CustomException(status=400, payload={"VMware": "Invalid operation."})

            return diskSpec
        except Exception as e:
            raise e



    def __buildNicSpec(self, data: dict) -> object:
        try:
            nicSpec = vim.vm.device.VirtualDeviceSpec()
            if data["operation"] == "edit":
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                if VirtualMachineSpecsBuilder.getEthernetDeviceType(data["device"]) == data["deviceType"]:
                    nicSpec.device = data["device"]
                else:
                    nicSpec.device = VirtualMachineSpecsBuilder.getEthernetDeviceInstance(data["deviceType"])
                    nicSpec.device.deviceInfo = vim.Description()
                    nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicSpec.device.connectable.startConnected = True
                    nicSpec.device.connectable.allowGuestControl = True
                    nicSpec.device.connectable.connected = False
                    nicSpec.device.connectable.status = 'untried'
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                if "deviceLabel" in data:
                    nicSpec.device.deviceInfo.label = data["deviceLabel"]
                nicSpec.device.backing = self.__buildNicBackingSpec(data["network"].oNetwork)
            elif data["operation"] == 'add':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                nicSpec.device = VirtualMachineSpecsBuilder.getEthernetDeviceInstance(data["deviceType"])
                nicSpec.device.deviceInfo = vim.Description()
                nicSpec.device.deviceInfo.summary = data["network"].oNetwork.name
                if "deviceLabel" in data:
                    nicSpec.device.deviceInfo.label = data["deviceLabel"]
                nicSpec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                nicSpec.device.connectable.startConnected = True
                nicSpec.device.connectable.allowGuestControl = True
                nicSpec.device.connectable.connected = False
                nicSpec.device.connectable.status = 'untried'
                nicSpec.device.backing = self.__buildNicBackingSpec(data["network"].oNetwork)
                if "additionalData" in data:
                    nicSpec.device.controllerKey = data["additionalData"]["controllerKey"]
                    nicSpec.device.unitNumber = data["additionalData"]["unitNumber"]

            elif data["operation"] == 'remove':
                nicSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                nicSpec.device = data["device"]
            else:
                raise CustomException(status=400, payload={"VMware": "Invalid operation."})

            return nicSpec
        except Exception as e:
            raise e



    def __buildExistentNetDevicesSpecs(self, templDevData: list) -> list:
        # Build the spec data structure for the devices present in the template.
        from vmware.models.VMware.Network import Network

        templDevsInfo = self.getNetworkInformation() # the network info of the template.
        devsSpecsData = list() # intermediate data structure.
        specsList = list() # real spec data obtained from  self.__buildNicSpec.

        try:
            for devData in templDevData:
                # Use label to find the right device.
                if "label" in devData and devData["label"]:
                    found = False
                    # Reverse the iterator to safely remove items from the same list that we are looping.
                    for devInfo in reversed(templDevsInfo):
                        if devInfo["label"] == devData["label"]:
                            found = True
                            if devInfo["deviceType"] == devData["deviceType"]: # Both the label and deviceType matches: device found ok.
                                devsSpecsData.append({
                                    "operation": "edit",
                                    "device": self.oNic(devInfo["label"]),
                                    "deviceLabel": devData["label"],
                                    "deviceType": devData["deviceType"],
                                    "network": Network(self.assetId, devData["networkMoId"])
                                })
                            else:
                                # The label matches but the device type is wrong. Cannot change it, so remove it and add a new one.
                                oldDev = self.oNic(devInfo["label"])
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
                        raise CustomException(status=400, payload={"VMware": "can't find the network card: "+str(devData["label"])+"."})

            # If there are some template devices without match in the input data, they should be removed.
            if templDevsInfo:
                for devInfo in templDevsInfo:
                    devsSpecsData.append({
                        "operation": "remove",
                        "device": self.oNic(devInfo["label"])
                    })

            for data in devsSpecsData:
                specsList.append(self.__buildNicSpec(data))

            return specsList
        except Exception as e:
            raise e



    def __buildNewNetDevicesSpecs(self, newDevData: list) -> list:
        # Build the spec data structure for the devices not present in the template.
        from vmware.models.VMware.Network import Network

        devsSpecsData = list() # intermediate data structure.
        specsList = list() # real spec data obtained from self.__buildNicSpec.

        try:
            # Build an intermediate data structure and pass it to self.__buildNicSpec to obtain the real spec data struct.
            for devData in newDevData:
                devsSpecsData.append({
                    "operation": "add",
                    "device": None,
                    "deviceLabel": "",
                    "deviceType": devData["deviceType"],
                    "network": Network(self.assetId, devData["networkMoId"])
                })

            for data in devsSpecsData:
                specsList.append(self.__buildNicSpec(data))

            return specsList
        except Exception as e:
            raise e



    def __buildExistentDiskDevicesSpecs(self, templDevData: list) -> list:
        # Build the spec data structure for the devices present in the template.
        from vmware.models.VMware.Datastore import Datastore

        templDevsInfo = self.getDisksInformation() # the disk info of the template.
        devsSpecsData = list() # intermediate data structure.
        specsList = list() # real spec data obtained from  self.__buildNicSpec.
        deviceKeysList = list() # list of the disks ids of the template.

        try:
            for devData in templDevData:
                # Use label to find the right device.
                if "label" in devData and devData["label"]:
                    found = False
                    # Reverse the iterator to safely remove items from the same list that we are looping.
                    for devInfo in reversed(templDevsInfo):
                        if devInfo["label"] == devData["label"]:
                            found = True
                            device = self.oDisk(devInfo["label"])
                            datastore = Datastore(self.assetId, devData["datastoreMoId"])
                            # If the disk is moving in another datastore, the filename of the template disk and the device key are needed also.
                            # The info should be passed to the disk locator spec field in the relocate spec.
                            filePath = device.backing.fileName # grab the disk filename from the template.
                            deviceKey = device.key # grab the disk key from the template.
                            devsSpecsData.append({
                                "operation": "edit",
                                "device": self.oDisk(devInfo["label"]),
                                "deviceLabel": devData["label"],
                                "deviceType": devData["deviceType"],
                                "sizeMB": devData["sizeMB"],
                                "datastore": datastore,
                                "filePath": filePath,
                                "deviceKey": deviceKey
                            })

                            # If there is a match, remove the element from the list.
                            templDevsInfo.remove(devInfo)
                            break

                    # Device not found: error in input data.
                    if not found:
                        raise CustomException(status=400, payload={"VMware": "can't find the disk: "+str(devData["label"])+"."})

            # If there are some template devices without match in the input data, they should be removed.
            if templDevsInfo:
                for devInfo in templDevsInfo:
                    devsSpecsData.append({
                        "operation": "remove",
                        "device": self.oDisk(devInfo["label"]),
                        "deviceKey": 0
                    })

            for data in devsSpecsData:
                spec = self.__buildDiskSpec(data)
                specsList.append(spec)

            return specsList
        except Exception as e:
            raise e



    def __buildNewDiskDevicesSpecs(self, newDevData: list, vmDatastoreMoId: list) -> list:
        # Build the spec data structure for the devices not present in the template.
        from vmware.models.VMware.Datastore import Datastore

        devsSpecsData = list() # intermediate data structure.
        specsList = list() # real spec data obtained from  self.__buildNicSpec.

        try:
            # Build an intermediate data structure and pass it to self.__buildNicSpec to obtain the real spec data struct.
            diskNumber = 0
            j = 0

            for devData in newDevData:
                dsStore = Datastore(self.assetId, devData["datastoreMoId"])
                # In many cases the datastore name of the new virtual disk is also needed in the filePath, with the naming convention [datastore_name].
                filePath = '['+dsStore.info()["name"]+']'
                controllerKey = self.oController().key
                diskNumber = self.__setDiskSlotNumber(diskNumber)
                devsSpecsData.append({
                    "operation": "add",
                    "device": None,
                    "deviceLabel": "",
                    "deviceType": devData["deviceType"],
                    "sizeMB": devData["sizeMB"],
                    "datastore": dsStore,
                    "filePath": filePath,
                    "newDiskNumber": diskNumber,
                    "controllerKey": controllerKey,
                    "deviceKey": 0
                })

                j += 1

            for data in devsSpecsData:
                spec = self.__buildDiskSpec(data)
                specsList.append(spec)

            return specsList
        except Exception as e:
            raise e



    def __buildDiskBackingSpec(self, spec: object, oDatastore: object, deviceType: str, filePath: str) -> object:
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
                spec.fileName = filePath

            return spec
        except Exception as e:
            raise e



    def __buildNicBackingSpec(self, portGroup: object):
        try:
            if isinstance(portGroup, vim.dvs.DistributedVirtualPortgroup):  # distributed port group
                backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
                backing.port = vim.dvs.PortConnection()
                backing.port.portgroupKey = portGroup.key
                backing.port.switchUuid = portGroup.config.distributedVirtualSwitch.uuid
            elif isinstance(portGroup, vim.OpaqueNetwork):  # third-party network
                backing = vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo()
                backing.opaqueNetworkType = portGroup.summary.opaqueNetworkType
                backing.opaqueNetworkId = portGroup.summary.opaqueNetworkId
            else: # standard port group
                backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                backing.deviceName = portGroup.name
                backing.network = portGroup

            return backing
        except Exception as e:
            raise e



    def __setDiskSlotNumber(self, unitNumber: int = 0) -> int:
        try:
            if unitNumber:
                unitNumber += 1 # avoid using the same unit number when adding more than one disk.
            for dev in self.oDevices():
                if hasattr(dev.backing, 'fileName'):
                    if int(dev.unitNumber) + 1 > unitNumber:
                        unitNumber = int(dev.unitNumber) + 1
            if unitNumber == 7: # unit number 7 is reserved for scsi controller.
                unitNumber += 1
            if unitNumber >= 16:
                raise CustomException(status=400, payload={"VMware": "too many virtual disks!"})

            return unitNumber
        except Exception as e:
            raise e
