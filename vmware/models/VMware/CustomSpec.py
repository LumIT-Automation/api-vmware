from vmware.models.VMware.backend.CustomSpecManager import CustomSpecManager as Backend
from vmware.helpers.Log import Log



class CustomSpec(Backend):
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(assetId, *args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    @staticmethod
    def info(assetId, specName) -> dict:
        dns = list()
        o = {
                "network": [],
                "hostName": "",
                "domainName": "",
                "timeZone": ""
            }

        try:
            specManager = CustomSpec(assetId)
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

                if dns:
                    o["dns1"] = dns[0]
                    if 1 < len(dns):
                        o["dns2"] = dns[1]

                if hasattr(spec.spec, "nicSettingMap") and spec.spec.nicSettingMap:
                    for nicSet in spec.spec.nicSettingMap:
                        if hasattr(nicSet, "adapter"):
                            nic = dict()
                            if hasattr(nicSet.adapter, "ip") and hasattr(nicSet.adapter.ip, "ipAddress"):
                                nic["ip"] = nicSet.adapter.ip.ipAddress
                            if hasattr(nicSet.adapter, "subnetMask"):
                                nic["netMask"] = nicSet.adapter.subnetMask
                            if hasattr(nicSet.adapter, "gateway"):
                                nic["gw"] = nicSet.adapter.gateway
                            # DNS settings for a single network card is available in the data structure but not from the vCenter interface.
                            #if hasattr(nicSet.adapter, "dnsServerList"):
                            #    nic["dns"] = nicSet.adapter.dnsServerList  # Overwrite global settings.
                            if nic:
                                o["network"].append(nic)

            return o
        except Exception as e:
            raise e



    @staticmethod
    def clone(assetId, sourceSpec: str, newSpec: str) -> None:
        try:
            specManager = CustomSpec(assetId)
            specManager.cloneoCustomSpec(sourceSpec, newSpec)
        except Exception as e:
            raise e



    @staticmethod
    def delete(assetId, specName) -> None:
        try:
            specManager = CustomSpec(assetId)
            specManager.deleteCustomSpec(specName)
        except Exception as e:
            raise e



    @staticmethod
    def modify(assetId, specName: str, data: dict) -> None:
        try:
            specManager = CustomSpec(assetId)
            specManager.editoCustomSpec(specName, data)

            specManager = CustomSpec(assetId)
            if specManager.oCustomSpecManager.DoesCustomizationSpecExist(specName):
                spec = specManager.oCustomSpecManager.GetCustomizationSpec(specName)
                specEdited = CustomSpec.replaceSpecObjectAttr(spec, data)
                specManager.oCustomSpecManager.OverwriteCustomizationSpec(specEdited)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> list:
        customSpecs = []

        try:
            for s in Backend(assetId).oCustomSpecs():
                customSpecs.append(s.name)

            return customSpecs
        except Exception as e:
            raise e
