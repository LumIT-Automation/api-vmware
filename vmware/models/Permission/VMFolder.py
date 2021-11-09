from django.db import connection

from vmware.models.VMware.VMFolder import VMFolder as VMwareVMFolder

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper



class VMFolder:
    def __init__(self, assetId: int, moId: str = "", vmFolderName: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.moId = moId
        self.name = vmFolderName



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exists(self) -> bool:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM `vmFolder` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])
            o = DBHelper.asDict(c)

            return bool(int(o[0]['c']))

        except Exception:
            return False
        finally:
            c.close()



    def info(self) -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT * FROM `vmFolder` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()
        try:
            c.execute("DELETE FROM `vmFolder` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def add(moId, assetId, vmFolderName) -> int:
        c = connection.cursor()

        # Check if assetId/vmFolderName is a valid VMware vmFolder (at the time of the insert).
        vmwareVMFolders = VMFolder.list(assetId)["data"]["items"]

        for v in vmwareVMFolders:
            if v["folder"] == moId and v["name"] == vmFolderName:
                try:
                    c.execute("INSERT INTO `vmFolder` (`moId`, `id_asset`, `name`) VALUES (%s, %s, %s)", [
                        moId,
                        assetId,
                        vmFolderName
                    ])

                    return c.lastrowid

                except Exception as e:
                    raise CustomException(status=400, payload={"database": e.__str__()})
                finally:
                    c.close()
