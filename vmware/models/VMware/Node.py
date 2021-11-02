import json

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.ApiSupplicant import ApiSupplicant


class Node:
    def __init__(self, assetId: int, vmFolderName: str, nodeName: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.vmFolderName = vmFolderName
        self.nodeName = nodeName



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data):
        try:
            vmware = Asset(self.assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/ltm/node/~"+self.vmFolderName+"~"+self.nodeName+"/",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            api.patch(
                additionalHeaders={
                    "Content-Type": "application/json",
                },
                data=json.dumps(data)
            )
        except Exception as e:
            raise e



    def delete(self):
        try:
            vmware = Asset(self.assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/ltm/node/~"+self.vmFolderName+"~"+self.nodeName+"/",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            api.delete(
                additionalHeaders={
                    "Content-Type": "application/json",
                }
            )
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, vmFolderName: str, silent: bool = False) -> dict:
        o = dict()

        try:
            vmware = Asset(assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/ltm/node/?$filter=vmFolder+eq+"+vmFolderName,
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"],
                silent=silent
            )

            o["data"] = api.get()
        except Exception as e:
            raise e

        return o



    @staticmethod
    def add(assetId: int, data: dict) -> None:
        try:
            vmware = Asset(assetId)
            asset = vmware.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"tm/ltm/node/",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            api.post(
                additionalHeaders={
                    "Content-Type": "application/json",
                },
                data=json.dumps(data)
            )
        except Exception as e:
            raise e


