from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


# In VMware, the CustomizationSpecManager is the (unique) Managed Object that can administer the virtual machines customization specifications.
# The customization specs are properties, not Managed Objects, so they don't have the moId.
#
# For documentation about VMware CustomSpecManager methods and properties:
# https://developer.vmware.com/apis/704/vsphere/vim.CustomizationSpecManager.html

class CustomSpecManager(VmwareContractor):



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def getCustomSpecInfo(assetId, specName, silent: bool = True) -> dict:
        o = {
            "ip": "",
            "netMask": "",
            "gw": [],
            "dns1": "",
            "dns2": "",
            "hostName": "",
            "domainName": "",
            "timeZone": "",
        }
        dns = list()

        try:
            spec = CustomSpecManager.getCustomSpecObject(assetId, specName, silent)
            if hasattr(spec, "spec"):
                if hasattr(spec.spec, "identity"):
                    if hasattr(spec.spec.identity, "hostName") and hasattr(spec.spec.identity.hostName, "name"):
                        o["hostName"] = spec.spec.identity.hostName.name
                    if hasattr(spec.spec.identity, "domain"):
                        o["domainName"] = spec.spec.identity.domain
                    if hasattr(spec.spec.identity, "timeZone"):
                        o["timeZone"] = spec.spec.identity.timeZone

                if hasattr(spec.spec, "globalIPSettings"):
                    if hasattr(spec.spec.globalIPSettings, "dnsServerList"):
                        dns = spec.spec.globalIPSettings.dnsServerList

                if hasattr(spec.spec, "nicSettingMap") and spec.spec.nicSettingMap and hasattr(spec.spec.nicSettingMap[0], "adapter"):
                    if hasattr(spec.spec.nicSettingMap[0].adapter, "ip") and hasattr(spec.spec.nicSettingMap[0].adapter.ip, "ipAddress"):
                        o["ip"] = spec.spec.nicSettingMap[0].adapter.ip.ipAddress
                    if hasattr(spec.spec.nicSettingMap[0].adapter, "subnetMask"):
                        o["netMask"] = spec.spec.nicSettingMap[0].adapter.subnetMask
                    if hasattr(spec.spec.nicSettingMap[0].adapter, "gateway"):
                        o["gw"] = spec.spec.nicSettingMap[0].adapter.gateway
                    if hasattr(spec.spec.nicSettingMap[0].adapter, "dnsServerList"):
                        dns = spec.spec.nicSettingMap[0].adapter.dnsServerList  # Overwrite global settings.
            if dns:
                o["dns1"] = dns[0]
                if 1 < len(dns):
                    o["dns2"] = dns[1]

            return o

        except Exception as e:
            raise e



    @staticmethod
    def cloneVMwareCustomSpec(assetId, data: dict, silent: bool = True) -> bool:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId, silent)
            if specManager.DoesCustomizationSpecExist(data["sourceSpec"]):
                specManager.DuplicateCustomizationSpec(name=data["sourceSpec"], newName=data["newSpec"])
            else:
                return False

        except Exception as e:
            raise e



    @staticmethod
    def deleteVMwareCustomSpec(assetId, specName, silent: bool = True) -> None:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId, silent)
            if specManager.DoesCustomizationSpecExist(specName):
                specManager.DeleteCustomizationSpec(specName)

        except Exception as e:
            raise e



    @staticmethod
    def overwriteVMwareCustomSpec(assetId, specName, data:dict, silent: bool = True) -> None:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId, silent)
            if specManager.DoesCustomizationSpecExist(specName):
                specManager.OverwriteCustomizationSpec(specName)

        except Exception as e:
            raise e



    # Full procedure: clone a spec and edit the new one.
    def editVMwareCustomSpec(assetId, specName, data: dict) -> None:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId)
            if specManager.DoesCustomizationSpecExist(specName):
                spec = specManager.GetCustomizationSpec(specName)
                specEdited = CustomSpecManager.replaceSpecObjectAttr(spec, data)
                specManager.OverwriteCustomizationSpec(specEdited)

        except Exception as e:
            raise e



    @staticmethod
    def getCustomSpecObject(assetId, specName, silent: bool = True) -> object:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId, silent)
            if specManager.DoesCustomizationSpecExist(specName):
                return specManager.GetCustomizationSpec(specName)
            else:
                return None

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



    # PlainvVirtual machines customization specifications list.
    @staticmethod
    def list(assetId, silent: bool = True) -> dict:
        customSpecs = []
        try:
            specObjList = CustomSpecManager.listCustomizationSpecObjects(assetId, silent)
            for spec in specObjList:
                customSpecs.append(spec.name)

            return dict({
                "items": customSpecs
            })

        except Exception as e:
            raise e



    # Virtual machines customization specifications objects list.
    @staticmethod
    def listCustomizationSpecObjects(assetId, silent: bool = True) -> list:
        try:
            specManager = CustomSpecManager.__getVMwareObject(assetId, silent)
            return specManager.info

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __getVMwareObject(assetId, silent: bool = True) -> object:
        try:
            vClient = VmwareContractor.connectToAssetAndGetContentStatic(assetId, silent)
            return vClient.oCluster.customizationSpecManager

        except Exception as e:
            raise e


