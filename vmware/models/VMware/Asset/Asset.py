from typing import List, Dict, Union

from dataclasses import dataclass

from vmware.repository.Asset import Asset as Repository


DataConnection: Dict[str, Union[str, int]] = {
    "address": "",
    "port": 443,
    "fqdn": "",
    "baseurl": "",
    "tlsverify": 1,
    "api_type": "",
    "api_additional_data": "",
    "username": "",
    "password": ""
}



class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(assetId)
        self.datacenter: str
        self.environment: str
        self.position: str
        self.connectionData: DataConnection = None

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
            from vmware.models.Permission.VObject import VObject
            VObject.add("any", aId, "any", "All the folders of this vCenter")
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
