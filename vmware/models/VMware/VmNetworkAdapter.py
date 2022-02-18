from vmware.models.VMware.Network import Network


class VmNetworkAdapter:
    def __init__(self, assetId: int, networkMoId: str, adapterLabel: str, deviceType: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.network: Network = Network(assetId, networkMoId)
        self.adapter = adapterLabel
        self.deviceType = deviceType



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self):
        try:
            return {
                "networkMoId": self.network.moId,
                "label": self.adapter,
                "deviceType": self.deviceType
            }
        except Exception as e:
            raise e
