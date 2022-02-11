from vmware.models.VMware.Network import Network


class VirtualMachineNetwork:
    # Virtual machine network adapter / attached network.

    def __init__(self, assetId: int, networkMoId: str, adapterLabel: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.network: Network = Network(assetId, networkMoId)
        self.adapter = adapterLabel



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self):
        try:
            return {
                "networkMoId": self.network.moId,
                "label": self.adapter
            }
        except Exception as e:
            raise e
