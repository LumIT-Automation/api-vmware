from typing import List

from vmware.repository.VMware.Asset.Asset import Asset as Repository


class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(assetId)
        self.address: str = ""
        self.port: int = 443
        self.fqdn: str = ""
        self.baseurl: str = ""
        self.tlsverify: int = 1
        self.api_type: str = ""
        self.api_additional_data: int = 1
        self.username: str = ""
        self.password: str = ""
        self.datacenter: str
        self.environment: str
        self.position: str

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def rawList() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            aId = Repository.add(data)

            # When inserting an asset, add the "any" vObject (Permission).
            from vmware.models.Permission.VObject import VObject
            VObject.add("any", aId, "any", "Any vCenter object")
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
