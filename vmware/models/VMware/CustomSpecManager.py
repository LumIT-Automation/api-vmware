from typing import List
from pyVmomi import vim

from vmware.models.VMware.backend.CustomSpecManager import CustomSpecManager as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

# In VMware, the CustomizationSpecManager is the (unique) Managed Object that can administer the virtual machines customization specifications.
class CustomSpecManager(Backend):
    def __init__(self, assetId: int, moId: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def info(assetId, specName) -> dict:
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
            specManager = CustomSpecManager(assetId)
            spec = specManager.oCustomSpec(specName)
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
    def clone(assetId, sourceSpec: str, newSpec: str) -> bool:
        try:
            specManager = CustomSpecManager(assetId)
            specManager.cloneoCustomSpec(sourceSpec, newSpec)

        except Exception as e:
            raise e



    @staticmethod
    def delete(assetId, specName) -> None:
        try:
            specManager = CustomSpecManager(assetId)
            specManager.deleteCustomSpec(specName)

        except Exception as e:
            raise e



    # Edit a spec.
    @staticmethod
    def modify(assetId, specName: str, data: dict) -> None:
        try:
            specManager = CustomSpecManager(assetId)
            specManager.editoCustomSpec(specName, data)

            specManager = CustomSpecManager(assetId)
            if specManager.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                spec = specManager.oCustomSpecManager.GetCustomizationSpec(specName)
                specEdited = CustomSpecManager.replaceSpecObjectAttr(spec, data)
                specManager.oCustomSpecManager.OverwriteCustomizationSpec(specEdited)

        except Exception as e:
            raise e



    # PlainvVirtual machines customization specifications list.
    @staticmethod
    def list(assetId) -> dict:
        customSpecs = []
        try:
            specManager = CustomSpecManager(assetId)
            specs = specManager.oCustomSpecs()
            for s in specs:
                customSpecs.append(s.name)

            return dict({
                "items": customSpecs
            })

        except Exception as e:
            raise e




