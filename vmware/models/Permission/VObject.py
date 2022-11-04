from typing import List

from vmware.models.VMware.FolderVM import FolderVM as vCenterVMFolder
from vmware.models.VMware.Network import Network as vCenterNetwork
from vmware.models.VMware.Datastore import Datastore as vCenterDatastore

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHelper import VmwareHelper

from vmware.models.Permission.repository.VObject import VObject as Repository


class VObject:
    def __init__(self, id: int = 0, assetId: int = 0, moId: str = "", name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.id_asset: int = int(assetId) # simple property, not composition.
        self.moId: str = moId
        self.name: str = name
        self.object_type: str = ""
        self.description: str

        self.__load()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def dataList() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(moId: str, assetId: int, objectName: str, description: str = "") -> int:
        oId = ""
        oName = ""
        objectType = VmwareHelper.getType(moId)

        # Check if the objectName exists in the vCenter. Skip for "any".
        if moId == "any":
            oId = "any"
            oName = "any"
        else:
            if objectType == 'folder':
                vCentervmObjects = vCenterVMFolder.list(assetId)
                for v in vCentervmObjects:
                    if v["moId"] == moId and v["name"] == objectName:
                        oId = v["moId"]
                        oName = v["name"]
                        break

            elif objectType == 'network':
                vCentervmObjects = vCenterNetwork.listQuick(assetId)
                for n in vCentervmObjects:
                    if n["moId"] == moId and n["name"] == objectName:
                        oId = n["moId"]
                        oName = n["name"]
                        break

            elif objectType == 'datastore':
                vCentervmObjects = vCenterDatastore.listQuick(assetId)
                for d in vCentervmObjects:
                    if d["moId"] == moId and d["name"] == objectName:
                        oId = d["moId"]
                        oName = d["name"]
                        break

        if not oId:
            raise CustomException(status=400, payload={"VMware": "object with given moId and name not found in vCenter"})

        try:
            return Repository.add(assetId, oId, oName, description)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(id=self.id, assetId=self.id_asset, moId=self.moId)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
