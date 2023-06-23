from typing import List

from vmware.models.VMware.Asset.repository.Asset import Asset as Repository

from vmware.helpers.Misc import Misc


class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(assetId)
        self.fqdn: str = ""
        self.protocol: str = "https"
        self.port: int = 443
        self.path: str = "/"
        self.tlsverify: bool = True
        self.baseurl: str = ""
        self.datacenter: str = ""
        self.environment: str = ""
        self.position: str = ""
        self.username: str = ""
        self.password: str = ""

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)

            for k, v in Misc.toDict(data).items():
                setattr(self, k, v)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
            del self
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
            info = Repository.get(self.id, showPassword=True)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
