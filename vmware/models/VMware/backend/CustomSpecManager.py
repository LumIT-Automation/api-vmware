from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log

class CustomSpecManager(VmwareHandler):
    def __init__(self, assetId: int, moId: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.oCustomSpecManager = self.__oCustomSpecManagerLoad()
        self.moId = self.oCustomSpecManager._GetMoId()



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
            if data["ip"]:
                newIp = vim.vm.customization.FixedIp()
                newIp.ipAddress = data["ip"]
                spec.spec.nicSettingMap[0].adapter.ip = newIp

            if data["netMask"]:
                spec.spec.nicSettingMap[0].adapter.subnetMask = data["netMask"]

            if data["gw"]:
                spec.spec.nicSettingMap[0].adapter.gateway = data["gw"]

            dns = []
            if data["dns1"]:
                dns.append(data["dns1"])

            if data["dns2"]:
                dns.append(data["dns2"])

            if dns:
                spec.spec.nicSettingMap[0].adapter.dnsServerList = dns
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
            return self._getSubContent('customizationSpecManager')
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
