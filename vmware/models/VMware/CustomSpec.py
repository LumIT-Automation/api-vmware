from typing import List
import string
import random

from vmware.models.VMware.backend.CustomSpecManager import CustomSpecManager as Backend
from vmware.helpers.Log import Log


NetInfo = {
    "ip": "",
    "netMask": "",
    "gw": []
}

class CustomSpec(Backend):
    def __init__(self, assetId: int, name: str = "", *args, **kwargs):
        super().__init__(assetId, *args, **kwargs)

        self.assetId: int = int(assetId)
        self.name: str = name
        self.dns1: str = ""
        self.dns2: str = ""
        self.hostName: str = ""
        self.domainName: str = ""
        self.timeZone: str = ""
        self.network: List[NetInfo] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        dns = list()
        o = {
            "assetId": self.assetId,
            "name": self.name,
            "network": [],
            "hostName": "",
            "domainName": "",
            "timeZone": ""
        }

        try:
            spec = self.oCustomSpec(self.name)

            if hasattr(spec, "info") and hasattr(spec.info, "type"):
                o["type"] = spec.info.type

                if o["type"] == "Linux":
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
                            if not o["domainName"]:
                                if hasattr(spec.spec.globalIPSettings, "dnsSuffixList"):
                                    o["domainName"] = spec.spec.globalIPSettings.dnsSuffixList[0]

                        if dns:
                            o["dns1"] = dns[0]
                            if 1 < len(dns):
                                o["dns2"] = dns[1]

                        if hasattr(spec.spec, "nicSettingMap") and spec.spec.nicSettingMap:
                            for nicSet in spec.spec.nicSettingMap:
                                if hasattr(nicSet, "adapter"):
                                    nic = {"gw": list()}
                                    if hasattr(nicSet.adapter, "ip"):
                                        if hasattr(nicSet.adapter.ip, "ipAddress"):
                                            nic["ip"] = nicSet.adapter.ip.ipAddress
                                            if hasattr(nicSet.adapter, "subnetMask"):
                                                nic["netMask"] = nicSet.adapter.subnetMask or ""
                                            if hasattr(nicSet.adapter, "gateway"):
                                                for el in nicSet.adapter.gateway:
                                                    nic["gw"].append(el)
                                        else:
                                            nic["dhcp"] = True
                                    if nic:
                                        o["network"].append(nic)

                elif o["type"] == "Windows":
                    if hasattr(spec, "spec"):
                        if hasattr(spec.spec, "identity"):
                            if hasattr(spec.spec.identity, "guiUnattended"):
                                if hasattr(spec.spec.identity.guiUnattended, "timeZone"):
                                    o["timeZone"] = spec.spec.identity.guiUnattended.timeZone
                            if hasattr(spec.spec.identity, "userData"):
                                if hasattr(spec.spec.identity.userData, "computerName"):
                                    if hasattr(spec.spec.identity.userData.computerName, "name"):
                                        o["hostName"] = spec.spec.identity.userData.computerName.name

                        if hasattr(spec.spec, "globalIPSettings"):
                            if hasattr(spec.spec.globalIPSettings, "dnsSuffixList"):
                                o["domainName"] = spec.spec.globalIPSettings.dnsSuffixList[0]

                        if hasattr(spec.spec, "nicSettingMap") and spec.spec.nicSettingMap:
                            for nicSet in spec.spec.nicSettingMap:
                                if hasattr(nicSet, "adapter"):
                                    nic = {"gw": list()}
                                    if hasattr(nicSet.adapter, "ip"):
                                        if hasattr(nicSet.adapter.ip, "ipAddress"):
                                            nic["ip"] = nicSet.adapter.ip.ipAddress
                                            if hasattr(nicSet.adapter, "subnetMask"):
                                                nic["netMask"] = nicSet.adapter.subnetMask or ""
                                            if hasattr(nicSet.adapter, "gateway"):
                                                for el in nicSet.adapter.gateway:
                                                    nic["gw"].append(el)
                                        else:
                                            nic["dhcp"] = True

                                    # Windows custom specs use DNS settings for single network cards.
                                    if hasattr(nicSet.adapter, "dnsServerList"):
                                        dns = nicSet.adapter.dnsServerList # overwrite global settings.
                                        if dns:
                                            if not "dns1" in o or not o["dns1"]:
                                                o["dns1"] = dns[0]
                                            if 1 < len(dns):
                                                if not "dns2" in o or not o["dns2"]:
                                                    o["dns2"] = dns[1]
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



    def cloneAndModify(self, data: dict) -> str:
        try:
            # Clone the customization specification in a new onr with a random name
            randStr = ''.join(random.choice(string.ascii_letters) for x in range(6))
            newSpecName = self.name+'-tmp-'+randStr
            self.clone(newSpecName)
            newSpec = CustomSpec(self.assetId, newSpecName)
            newSpec.modify(data) # edit the new custom spec.

            return newSpecName
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            self.deleteCustomSpec(self.name)
        except Exception as e:
            raise e



    def customizeGuestOS(self, oVirtualMachine: object) -> str:
        try:
            return self.customizeVMGuestOS(oVirtualMachine=oVirtualMachine, specName=self.name)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> list:
        customSpecs = list()

        try:
            for s in Backend(assetId).oCustomSpecs():
                customSpecs.append(
                    CustomSpec(assetId, s.name).info()
                )

            return customSpecs
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        customSpecs = list()

        try:
            for o in Backend(assetId).oCustomSpecs():
                customSpecs.append({
                    "assetId": assetId,
                    "name": o.name
                })

            return customSpecs
        except Exception as e:
            raise e
