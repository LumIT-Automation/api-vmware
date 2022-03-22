from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.Permission import Permission
from vmware.models.Permission.VMObject import VMObject as PermissionVMObject

from vmware.serializers.Permission.VMObject import PermissionVMObjectSerializer as Serializer
from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log



class PermissionVMObjectController(CustomController):
    @staticmethod
    def delete(request: Request, objectId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_vmobject_delete") or user["authDisabled"]:
                Log.actionLog("Permission vmware object deletion ", user)

                PermissionVMObject.delete(objectId)

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, objectId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission__vmobject_patch") or user["authDisabled"]:
                Log.actionLog("Permission vmware object modification ", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data, partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data["data"]

                    PermissionVMObject.modify(
                        objectId=objectId,
                        data=data
                    )

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "VMware": {
                            "error": str(serializer.errors)
                        }
                    }

                    Log.actionLog("User data incorrect: "+str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
