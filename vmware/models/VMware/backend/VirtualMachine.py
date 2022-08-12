from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


from vmware.helpers.Log import Log


class VirtualMachine(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

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



    def oDisk(self, diskLabel):
        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == diskLabel:
                    return dev
            raise CustomException(status=400, payload={"VMware": "can't find the disk "+str(diskLabel)+"."})
        except Exception as e:
            raise e



    def getDisksInformation(self) -> list:
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



    def oNic(self, nicLabel):
        try:
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualEthernetCard) and dev.deviceInfo.label == nicLabel:
                    return dev
            raise CustomException(status=400, payload={"VMware": "can't find the network card: "+str(nicLabel)+"."})
        except Exception as e:
            raise e



    def guestInfo(self) -> dict:
        info = {
            "network": {},
            "dnsConfig": {},
            "vmTools": {}
        }

        try:
            infoData = self.oVirtualMachine.guest

            if hasattr(infoData, "guestFamily"):
                info["guestOS"] = infoData.guestFamily
            if hasattr(infoData, "hostName"):
                info["hostname"] = infoData.hostName

            if hasattr(infoData, "toolsVersion"):
                info["vmTools"]["version"] = infoData.toolsVersion
            if hasattr(infoData, "toolsInstallType"):
                info["vmTools"]["type"] = infoData.toolsInstallType
            if hasattr(infoData, "toolsStatus"):
                info["vmTools"]["status"] = infoData.toolsStatus
            if hasattr(infoData, "toolsRunningStatus"):
                info["vmTools"]["runningStatus"] = infoData.toolsRunningStatus

            if hasattr(infoData, "ipStack"):
                if infoData.ipStack and hasattr(infoData.ipStack[0], "dnsConfig"):
                    if infoData.ipStack[0].dnsConfig:
                        if hasattr(infoData.ipStack[0].dnsConfig, "ipAddress"):
                            info["dnsConfig"]["dnsList"] = infoData.ipStack[0].dnsConfig.ipAddress
                        if hasattr(infoData.ipStack[0].dnsConfig, "domainName"):
                            info["dnsConfig"]["domain"] = infoData.ipStack[0].dnsConfig.domainName
                        if hasattr(infoData.ipStack[0].dnsConfig, "searchDomain"):
                            info["dnsConfig"]["searchDomain"] = infoData.ipStack[0].dnsConfig.searchDomain

            for nic in self.oVirtualMachine.guest.net:
                if hasattr(nic, "network") and nic.network:
                    info["network"][nic.network] = []
                    for ip in nic.ipAddress:
                        info["network"][nic.network] .append(ip)

            return info
        except Exception as e:
            raise e



    def getNetworkInformation(self) -> list:
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



    def oController(self) -> str:
        try:
            # Get the first controller device.
            controller = None
            for dev in self.oDevices():
                if isinstance(dev, vim.vm.device.VirtualSCSIController):
                    controller = dev
                    break
            if not controller:
                raise CustomException(status=400, payload={"VMware": "controller not found!"})

            return controller
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
            return VmwareHandler().getObjects(assetId=assetId, vimType=vim.VirtualMachine)
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
            return self.getObjects(assetId=self.assetId, vimType=vim.VirtualMachine, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "cannot load resource."})
