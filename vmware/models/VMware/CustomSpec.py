from vmware.models.VMware.backend.CustomSpecManager import CustomSpecManager as Backend
from vmware.helpers.Log import Log


class CustomSpec(Backend):
    def __init__(self, assetId: int, name: str = "", *args, **kwargs):
        super().__init__(assetId, *args, **kwargs)

        self.assetId: int = int(assetId)
        self.name: str = name



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def raw(self) -> object:
        try:
            return self.oCustomSpec(self.name)
        except Exception as e:
            raise e



    def info(self) -> dict:
        dns = list()
        o = {
                "network": [],
                "hostName": "",
                "domainName": "",
                "timeZone": ""
            }

        try:
            spec = self.raw()

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
                            #    nic["dns"] = nicSet.adapter.dnsServerList # overwrite global settings.
                            if nic:
                                o["network"].append(nic)

            return o
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            self.editCustomSpec(self.name, data)
        except Exception as e:
            raise e



    def clone(self, newSpec: str) -> None:
        try:
            self.cloneCustomSpec(self.name, newSpec)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            self.deleteCustomSpec(self.name)
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
