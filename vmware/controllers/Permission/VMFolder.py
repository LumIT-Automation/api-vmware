from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.Permission import Permission
from vmware.models.Permission.VMFolder import VMFolder as PermissionVMFolder

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log



class PermissionVMFolderController(CustomController):
    @staticmethod
    def delete(request: Request, assetId: int, moId: str) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_vmfolder_delete") or user["authDisabled"]:
                Log.actionLog("Permission vmFolder cleanup from database", user)

                f = PermissionVMFolder(assetId, moId)
                f.delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

