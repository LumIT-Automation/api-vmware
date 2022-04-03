from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


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
                raise CustomException(status=404, payload={"VMware": "cannot load resource."})
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
                raise CustomException(status=404, payload={"VMware": "cannot load resource."})
        except Exception as e:
            raise e



    def deleteCustomSpec(self, name: str) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(name):
                self.oCustomSpecManager.DeleteCustomizationSpec(name)
            else:
                raise CustomException(status=404, payload={"VMware": "cannot load resource."})
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
        n = 0
        if spec.info.type == "Linux":
            if "network" in data and data["network"]:
                for netSet in data["network"]:
                    if netSet["ip"]:
                        if not hasattr(spec.spec, 'nicSettingMap'):
                            spec.spec.nicSettingMap = []
                        if len(spec.spec.nicSettingMap) <= n:
                            spec.spec.nicSettingMap.append(vim.vm.customization.AdapterMapping())
                        if not hasattr(spec.spec.nicSettingMap[n], 'adapter') or not spec.spec.nicSettingMap[n].adapter:
                            spec.spec.nicSettingMap[n].adapter = vim.vm.customization.IPSettings()
                        if not hasattr(spec.spec.nicSettingMap[n].adapter, 'ip') or not isinstance(
                                spec.spec.nicSettingMap[n].adapter, vim.vm.customization.FixedIp):
                            spec.spec.nicSettingMap[n].adapter.ip = vim.vm.customization.FixedIp()
                        spec.spec.nicSettingMap[n].adapter.ip.ipAddress = netSet["ip"]
                    if netSet["netMask"]:
                        spec.spec.nicSettingMap[n].adapter.subnetMask = netSet["netMask"]
                    if netSet["gw"]:
                        spec.spec.nicSettingMap[n].adapter.gateway = netSet["gw"]
                    # spec.spec.nicSettingMap[n].adapter.dnsServerList = dnsList
                    n += 1

            dns = []
            if "dns1" in data and data["dns1"]:
                dns.append(data["dns1"])
            if "dns2" in data and data["dns2"]:
                dns.append(data["dns2"])
            if dns:
                spec.spec.globalIPSettings.dnsServerList = dns

            if "hostName" in data and data["hostName"]:
                newComputerName = vim.vm.customization.FixedName()
                newComputerName.name = data["hostName"]
                spec.spec.identity.hostName = newComputerName

            if "domainName" in data and data["domainName"]:
                spec.spec.identity.domain = data["domainName"]
                spec.spec.globalIPSettings.dnsSuffixList = [data["domainName"]]

            if "timeZone" in data and data["timeZone"]:
                spec.spec.identity.timeZone = data["timeZone"]

        return spec
