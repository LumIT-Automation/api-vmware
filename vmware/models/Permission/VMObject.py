from typing import List

from vmware.models.VMware.VMFolder import VMFolder as vCenterVMFolder
from vmware.models.VMware.Network import Network as vCenterNetwork
from vmware.models.VMware.Datastore import Datastore as vCenterDatastore

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log

from vmware.repository.VMObject import VMObject as Repository


class VMObject:
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int
        self.id_asset: int = assetId
        self.moId: str = moId
        self.name: str = name
        self.description: str



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(
                self.id_asset,
                self.moId,
                VMObject.getType # Callable[[str], str].
            )
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id_asset, self.moId)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(moId: str, assetId: int, objectName: str, description: str = "") -> int:
        oId = ""
        oName = ""
        objectType = VMObject.getType(moId)

        # Check if the objectName exists in the vCenter. Skip for "any".
        if moId == "any":
            oId = "any"
            oName = "any"
        else:
            if objectType == 'folder':
                vCentervmObjects = vCenterVMFolder.list(assetId)["items"]
                for v in vCentervmObjects:
                    if v["moId"] == moId and v["name"] == objectName:
                        oId = v["moId"]
                        oName = v["name"]
                        break

            elif objectType == 'network':
                vCentervmObjects = vCenterNetwork.list(assetId)["items"]
                for n in vCentervmObjects:
                    if n["moId"] == moId and n["name"] == objectName:
                        oId = n["moId"]
                        oName = n["name"]
                        break

            elif objectType == 'datastore':
                vCentervmObjects = vCenterDatastore.list(assetId)["items"]
                for d in vCentervmObjects:
                    if d["moId"] == moId and d["name"] == objectName:
                        oId = d["moId"]
                        oName = d["name"]
                        break

        if not oId:
            raise CustomException(status=400, payload={"VMware": "Object with given moId and name not found in vCenter"})

        try:
            return Repository.add(assetId, oId, oName, description)
        except Exception as e:
            raise e



    @staticmethod
    def getType(moId: str) -> str:
        objectType = ""

        try:
            moIdPrefix = moId.split('-')[0]
            if moIdPrefix == "group":
                objectType = "folder"
            elif moIdPrefix == "datastore":
                objectType = "datastore"
            elif moIdPrefix == "network" or moIdPrefix == "dvportgroup":
                objectType = "network"

            return objectType
        except Exception:
            raise CustomException(status=400, payload={"VMware": "Object type not found. Wrong moId?"})
