from typing import List

from dataclasses import dataclass

from vmware.repository.Asset import Asset as Repository


@dataclass
class DataConnection:
    address: str
    port: int
    fqdn: str
    baseurl: str
    tlsverify: int
    api_type: str
    api_additional_data: str
    username: str
    password: str



class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(assetId)
        self.datacenter: str
        self.environment: str
        self.position: str
        self.dataConnection: DataConnection

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

            # When inserting an asset, add the "any" vmObject (Permission).
            from vmware.models.Permission.VMObject import VMObject
            VMObject.add("any", aId, "any", "All the folders of this vCenter")
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
        except Exception:
            pass
