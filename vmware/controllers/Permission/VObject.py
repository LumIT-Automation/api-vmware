from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.Permission import Permission
from vmware.models.Permission.VObject import VObject as PermissionVMObject

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class PermissionVObjectController(CustomController):
    @staticmethod
    def delete(request: Request, objectId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_vmobject_delete") or user["authDisabled"]:
                Log.actionLog("Permission vmware object deletion ", user)

                PermissionVMObject(id=objectId).delete()
                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
