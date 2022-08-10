from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log



class CustomSpecManager(VmwareHandler):
    # In VMware, the CustomizationSpecManager is the (unique) Managed Object
    # that can administer the virtual machines customization specifications.

    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.oCustomSpecManager = self.__oCustomSpecManagerLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oCustomSpec(self, name) -> object:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(name):
                return self.oCustomSpecManager.GetCustomizationSpec(name=name)
            else:
                raise CustomException(status=404, payload={"VMware": "cannot load specified customization specification."})
        except Exception as e:
            raise e



    def oCustomSpecs(self) -> list:
        try:
            return self.oCustomSpecManager.info
        except Exception as e:
            raise e



    def cloneCustomSpec(self, srcSpecName: str, newSpecName: str) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(srcSpecName):
                self.oCustomSpecManager.DuplicateCustomizationSpec(name=srcSpecName, newName=newSpecName)
            else:
                raise CustomException(status=404, payload={"VMware": "cannot load specified customization specification."})
        except Exception as e:
            raise e



    def deleteCustomSpec(self, name: str) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(name):
                self.oCustomSpecManager.DeleteCustomizationSpec(name)
            else:
                raise CustomException(status=404, payload={"VMware": "cannot load specified customization specification."})
        except Exception as e:
            raise e



    def editCustomSpec(self, specName: str, data: dict) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                spec = self.oCustomSpec(specName)
                specEdited = CustomSpecManager.__replaceSpecObjectAttr(spec, data)

                self.oCustomSpecManager.OverwriteCustomizationSpec(specEdited)
        except Exception as e:
            raise e



    def customizeVMGuestOS(self, oVirtualMachine: object, specName: str) -> str:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                spec = self.oCustomSpec(specName)
                task = oVirtualMachine.CustomizeVM_Task(spec.spec)
                return task._GetMoId()
            else:
                raise CustomException(status=404, payload={"VMware": "cannot load specified customization specification."})
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oCustomSpecManagerLoad(self):
        try:
            return self.getCustomizationSpecManager(assetId=self.assetId)
        except Exception:
            raise CustomException(status=404, payload={"VMware": "cannot load resource."})



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __replaceSpecObjectAttr(spec, data: dict):
        try:
            if spec.info.type == "Linux" or spec.info.type == "Windows":
                if "network" in data and data["network"]:
                    n = 0
                    for netSet in data["network"]:
                        if "ip" in netSet:
                            if not hasattr(spec.spec, 'nicSettingMap'):
                                spec.spec.nicSettingMap = []
                            if len(spec.spec.nicSettingMap) <= n:
                                spec.spec.nicSettingMap.append(vim.vm.customization.AdapterMapping())
                            if not hasattr(spec.spec.nicSettingMap[n], 'adapter') or not spec.spec.nicSettingMap[n].adapter:
                                spec.spec.nicSettingMap[n].adapter = vim.vm.customization.IPSettings()

                            if "dhcp" in netSet and netSet["dhcp"]: # bool.
                                if not hasattr(spec.spec.nicSettingMap[n].adapter, 'ip') or not isinstance(
                                        spec.spec.nicSettingMap[n].adapter, vim.vm.customization.DhcpIpGenerator):
                                    spec.spec.nicSettingMap[n].adapter.ip = vim.vm.customization.DhcpIpGenerator()
                            else:
                                if not hasattr(spec.spec.nicSettingMap[n].adapter, 'ip') or not isinstance(
                                            spec.spec.nicSettingMap[n].adapter, vim.vm.customization.FixedIp):
                                    spec.spec.nicSettingMap[n].adapter.ip = vim.vm.customization.FixedIp()
                                spec.spec.nicSettingMap[n].adapter.ip.ipAddress = netSet["ip"]
                                if "netMask" in netSet and netSet["netMask"]:
                                    spec.spec.nicSettingMap[n].adapter.subnetMask = netSet["netMask"]
                                if "gw" in netSet and netSet["gw"]:
                                    spec.spec.nicSettingMap[n].adapter.gateway = netSet["gw"]
                        n += 1
                    # If there are more nics in the original customSpec than in the new one, remove all the  exceeding elements
                    # (use reverse order to remove the elements).
                    if len(spec.spec.nicSettingMap) > n:
                        for i in range(len(spec.spec.nicSettingMap) - 1, n - 1, -1):
                            spec.spec.nicSettingMap.pop(i)

                if "domainName" in data and data["domainName"]:
                    if hasattr(spec.spec.identity, "domain"):
                        spec.spec.identity.domain = data["domainName"] # Linux only.
                    spec.spec.globalIPSettings.dnsSuffixList = [data["domainName"]]

                # DNS data. Stored in different places depending on whether it is a Linux or Windows custom spec.
                dns = []
                if "dns1" in data and data["dns1"]:
                    dns.append(data["dns1"])
                if "dns2" in data and data["dns2"]:
                    dns.append(data["dns2"])

                if spec.info.type == "Linux":
                    if dns:
                        spec.spec.globalIPSettings.dnsServerList = dns
                    if "hostName" in data and data["hostName"]:
                        newComputerName = vim.vm.customization.FixedName()
                        newComputerName.name = data["hostName"]
                        spec.spec.identity.hostName = newComputerName

                    if "timeZone" in data and data["timeZone"]:
                        spec.spec.identity.timeZone = data["timeZone"]

                if spec.info.type == "Windows":
                    if "hostName" in data and data["hostName"]:
                        if not hasattr(spec.spec.identity, "userData"):
                            spec.spec.identity.userData = vim.vm.customization.UserData()
                        newComputerName = vim.vm.customization.FixedName()
                        newComputerName.name = data["hostName"]
                        spec.spec.identity.userData.computerName = newComputerName
                    # Use first adapter to store dns info.
                    if dns:
                        spec.spec.nicSettingMap[0].adapter.dnsServerList = dns

            return spec
        except Exception as e:
            raise e