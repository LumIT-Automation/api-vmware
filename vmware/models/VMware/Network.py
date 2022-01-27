from typing import List


from vmware.models.VMware.backend.Network import Network as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper


class Network(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name

        self.cHostSystems: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadConfiguredHostSystems(self) -> None:
        from vmware.models.VMware.HostSystem import HostSystem
        # Load VMware hostsystems objects.
        try:
            for h in self.oHostSystems():
                cfH = VmwareHelper.vmwareObjToDict(h)

                self.cHostSystems.append(
                    HostSystem(self.assetId, cfH["moId"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True) -> dict:
        hosts = list()
        netInfo = dict()
        try:
            netSummary = self.oSummaryLoad()
            netInfo["name"] = netSummary.name
            netInfo["accessible"] = netSummary.accessible
            self.loadConfiguredHostSystems()

            for h in self.cHostSystems:
                hInfo = h.info(False)

                # Remove some related objects' information, if not loaded.
                #if not c["networks"]:
                #    del(c["networks"])

                hosts.append(hInfo)

            return {
                "networkInfo": netInfo,
                "configuredHosts": hosts
            }
        except Exception as e:
            raise e

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId) -> List[dict]:
        networks = list()

        try:
            for n in Backend.oNetworks(assetId):
                data = {"assetId": assetId}
                data.update(VmwareHelper.vmwareObjToDict(n))
                networks.append(data)

            return networks
        except Exception as e:
            raise e




