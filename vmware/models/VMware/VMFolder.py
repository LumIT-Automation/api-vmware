from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.ApiSupplicant import ApiSupplicant


class VMFolder:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> dict:
        o = dict()

        try:
            vmware = Asset(assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/auth/vmFolder/",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            o["data"] = api.get()
        except Exception as e:
            raise e

        return o
