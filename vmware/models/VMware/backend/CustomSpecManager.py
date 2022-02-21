from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


class CustomSpecManager(VmwareHandler):
    # In VMware, the CustomizationSpecManager is the (unique) Managed Object
    # that can administer the virtual machines customization specifications.

    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(assetId, *args, **kwargs)

        self.assetId = int(assetId)
        self.oCustomSpecManager = self.__oCustomSpecManagerLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oCustomSpec(self, name) -> object:
        try:
            return self.oCustomSpecManager.GetCustomizationSpec(name=name)
        except Exception as e:
            raise e



    def oCustomSpecs(self) -> list:
        try:
            return self.oCustomSpecManager.info
        except Exception as e:
            raise e



    def cloneoCustomSpec(self, srcSpecName: str, newSpecName: str) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(srcSpecName):
                self.oCustomSpecManager.DuplicateCustomizationSpec(name=srcSpecName, newName=newSpecName)

        except Exception as e:
            raise e



    def editoCustomSpec(self, specName: str, data: dict) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                spec = self.oCustomSpec(specName)
                specEdited = CustomSpecManager.replaceSpecObjectAttr(spec, data)
                self.oCustomSpecManager.OverwriteCustomizationSpec(specEdited)

        except Exception as e:
            raise e



    def deleteCustomSpec(self, specName) -> None:
        try:
            if self.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                self.oCustomSpecManager.DeleteCustomizationSpec(specName)

        except Exception as e:
            raise e



    # Edit attributes of a VMware customization specification.
    @staticmethod
    def replaceSpecObjectAttr(spec, data: dict):
        if spec.info.type == "Linux":
            if data["network"]:
                n = 0
                for netSet in data["network"]:
                    if netSet["ip"]:
                        if not hasattr(spec.spec, 'nicSettingMap'):
                            spec.spec.nicSettingMap = []
                        if len(spec.spec.nicSettingMap) <= n:
                            spec.spec.nicSettingMap.append(vim.vm.customization.AdapterMapping())
                        if not hasattr(spec.spec.nicSettingMap[n], 'adapter') or not spec.spec.nicSettingMap[n].adapter:
                            spec.spec.nicSettingMap[n].adapter = vim.vm.customization.IPSettings()
                        if not hasattr(spec.spec.nicSettingMap[n].adapter, 'ip') or not isinstance(spec.spec.nicSettingMap[n].adapter, vim.vm.customization.FixedIp):
                            spec.spec.nicSettingMap[n].adapter.ip = vim.vm.customization.FixedIp()
                        spec.spec.nicSettingMap[n].adapter.ip.ipAddress = netSet["ip"]
                    if netSet["netMask"]:
                        spec.spec.nicSettingMap[n].adapter.subnetMask = netSet["netMask"]
                    if netSet["gw"]:
                        spec.spec.nicSettingMap[n].adapter.gateway = netSet["gw"]
                    # spec.spec.nicSettingMap[n].adapter.dnsServerList = dnsList
                    n += 1

            dns = []
            if data["dns1"]:
                dns.append(data["dns1"])
            if data["dns2"]:
                dns.append(data["dns2"])
            if dns:
                spec.spec.globalIPSettings.dnsServerList = dns

            if data["hostName"]:
                newComputerName = vim.vm.customization.FixedName()
                newComputerName.name = data["hostName"]
                spec.spec.identity.hostName = newComputerName

            if data["domainName"]:
                spec.spec.identity.domain = data["domainName"]
                spec.spec.globalIPSettings.dnsSuffixList = [ data["domainName"] ]

            if data["timeZone"]:
                spec.spec.identity.timeZone = data["timeZone"]

        return spec



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oCustomSpecManagerLoad(self):
        try:
            return self.getSubContent('customizationSpecManager')
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
