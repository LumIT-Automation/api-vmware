from pyVmomi import vim

from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VirtualMachineSpecsBuilder(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def buildNetworkSpec(self, devicesData: dict) -> list:
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
        specsList = list()

        try:
            if "existent" in devicesData:
                specsList.extend(self.__buildExistentNetDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                specsList.extend(self.__buildNewNetDevicesSpecs(devicesData["new"]))

            return specsList
        except Exception as e:
            raise e



    def buildStorageSpec(self, devicesData: dict, vmDatastoreMoId: list) -> list:
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
        specsList = list()

        try:
            if "existent" in devicesData:
                specsList.extend(self.__buildExistentDiskDevicesSpecs(devicesData["existent"]))
            if "new" in devicesData:
                specsList.extend(self.__buildNewDiskDevicesSpecs(devicesData["new"], vmDatastoreMoId))

            return specsList
        except Exception as e:
            raise e



    def buildVMCloneSpecs(self, oDatastore: object, data: dict, cluster: object = None, host: object = None, devsSpecs: object = None, oCustomSpec: object = None):
        try:
            cloneSpec = vim.vm.CloneSpec()  # virtual machine specifications for a clone operation.

            # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
            relocateSpec = vim.vm.RelocateSpec()
            relocateSpec.datastore = oDatastore
            if cluster:
                relocateSpec.pool = cluster.oCluster.resourcePool # The resource pool associated to this cluster.
                if host:
                    relocateSpec.host = host.oHostSystem
            elif host:
                relocateSpec.pool = host.oHostSystem.parent.resourcePool # Standalone host resource pool.
                relocateSpec.host = host.oHostSystem
            else:
                raise CustomException(status=400, payload={"VMware": "missing both cluster and host params."})

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



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __buildDiskSpec(self, data: dict) -> object:
        try:
            diskSpec = vim.vm.device.VirtualDeviceSpec()
            if data["operation"] == "edit":
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                diskSpec.device = data["device"]
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1000 # MB, not MiB.
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1000 * 1000

                backingSpec = diskSpec.device.backing
                diskSpec.device.backing = self.__buildDiskBackingSpec(
                    spec=backingSpec,
                    oDatastore=data["datastore"].oDatastore,
                    deviceType=data["deviceType"],
                    filePath=data["filePath"]
                )

            elif data["operation"] == 'add':
                diskSpec.fileOperation = "create"
                diskSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                diskSpec.device = vim.vm.device.VirtualDisk()
                diskSpec.device.capacityInKB = int(data["sizeMB"]) * 1000
                diskSpec.device.capacityInBytes = int(data["sizeMB"]) * 1000 * 1000
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
                raise CustomException(status=400, payload={"VMware": "__buildDiskSpec: not an operation."})

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
                nicSpec.device = VirtualMachineSpecsBuilder.getEthernetDeviceInstance(data["deviceType"])
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
                raise CustomException(status=400, payload={"VMware": "__buildNicSpec: not an operation."})

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
                        raise CustomException(status=400, payload={"VMware": "__buildExistentNetDevicesSpecs: Can't find the network card: \"" + str(devData["label"]) + "\"."})

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
                    "deviceLabel": devData["label"],
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
                            filePath = ""
                            # If the disk is moving in another datastore, the datastore name in the filePath is also needed.
                            if devData["datastoreMoId"] != device.backing.datastore._GetMoId():
                                filePath = datastore.info()["name"]
                            devsSpecsData.append({
                                "operation": "edit",
                                "device": self.oDisk(devInfo["label"]),
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
                        raise CustomException(status=400, payload={"VMware": "__buildExistentDiskDevicesSpecs: Can't find the disk: \"" + str(devData["label"]) + "\"."})

            # If there are some template devices without match in the input data, they should be removed.
            if templDevsInfo:
                for devInfo in templDevsInfo:
                    devsSpecsData.append({
                        "operation": "remove",
                        "device": self.oDisk(devInfo["label"])
                    })

            for data in devsSpecsData:
                specsList.append(self.__buildDiskSpec(data))

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
                # If the disk is not in the default datastore of the VM, the datastore name in the filePath is also needed.
                filePath = ""
                if devData["datastoreMoId"] != vmDatastoreMoId[j]:
                    filePath = dsStore.info()["name"]
                controllerKey = self.oController().key
                diskNumber = self.__setDiskSlotNumber(diskNumber)
                devsSpecsData.append({
                    "operation": "add",
                    "device": None,
                    "deviceLabel": devData["label"],
                    "deviceType": devData["deviceType"],
                    "sizeMB": devData["sizeMB"],
                    "datastore": dsStore,
                    "filePath": filePath,
                    "newDiskNumber": diskNumber,
                    "controllerKey": controllerKey
                })

                j += 1

            for data in devsSpecsData:
                specsList.append(self.__buildDiskSpec(data))

            return specsList
        except Exception as e:
            raise e



    def __buildDiskBackingSpec(self, spec: object, oDatastore: object, deviceType: str, filePath: str):
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
