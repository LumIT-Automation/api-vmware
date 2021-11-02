from django.db import connection

from vmware.models.VMware.VMFolder import VMFolder as VMwareVMFolder

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper



class VMFolder:
    def __init__(self, assetId: int, vmFolderId: int = 0, vmFolderName: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.vmFolderId = id
        self.vmFolderName = vmFolderName



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exists(self) -> bool:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM `vmFolder` WHERE `vmFolder` = %s AND id_asset = %s", [
                self.vmFolderName,
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
            c.execute("SELECT * FROM `vmFolder` WHERE `vmFolder` = %s AND id_asset = %s", [
                self.vmFolderName,
                self.assetId
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()
        try:
            c.execute("DELETE FROM `vmFolder` WHERE `vmFolder` = %s AND id_asset = %s", [
                self.vmFolderName,
                self.assetId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def add(assetId, vmFolderName) -> int:
        c = connection.cursor()

        if vmFolderName == "any":
            try:
                c.execute("INSERT INTO `vmFolder` (id_asset, `vmFolder`) VALUES (%s, %s)", [
                    assetId,
                    vmFolderName
                ])

                return c.lastrowid

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()

        else:
            # Check if assetId/vmFolderName is a valid VMware vmFolder (at the time of the insert).
            vmwareVMFolders = VMwareVMFolder.list(assetId)["data"]["items"]

            for v in vmwareVMFolders:
                if v["name"] == vmFolderName:
                    try:
                        c.execute("INSERT INTO `vmFolder` (id_asset, `vmFolder`) VALUES (%s, %s)", [
                            assetId,
                            vmFolderName
                        ])

                        return c.lastrowid

                    except Exception as e:
                        raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
                    finally:
                        c.close()
