from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Permission.Permission import Permission
from vmware.serializers.Stage2.BoostrapKey import Stage2BootstrapKeySerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2BootstrapKeyController(CustomController):
    @staticmethod
    def delete(request: Request, keyId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="bootstrap_key_delete") or user["authDisabled"]:
                Log.actionLog("Second stage bootstrap key deletion", user)

                key = BootstrapKey(keyId)
                key.delete()

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
    def patch(request: Request, keyId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="bootstrap_key_patch") or user["authDisabled"]:
                Log.actionLog("Second stage bootstrap key modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    key = BootstrapKey(keyId)
                    key.modify(data)

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

