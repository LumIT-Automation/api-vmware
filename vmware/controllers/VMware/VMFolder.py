from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VMFolder import VMFolder
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VMFolders import VMwareVMFoldersSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVMFolderController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str) -> Response:
        data = {
            "data": {
                "parentList": []
            }
        }
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="folder_get", assetId=assetId, folderMoId=moId) or user["authDisabled"]:
                Log.actionLog("VMFolder properties", user)

                lock = Lock("vmFolder", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    vmFolder = VMFolder(assetId, moId)

                    data["data"]["parentList"] = vmFolder.parentList()
                    data["href"] = request.get_full_path()

                    httpStatus = status.HTTP_200_OK
                    lock.release()

                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED

            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("vmFolder", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
