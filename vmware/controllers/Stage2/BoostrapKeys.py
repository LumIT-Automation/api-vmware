from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Permission.Permission import Permission

from vmware.serializers.Stage2.BoostrapKeys import Stage2BootstrapKeysSerializer as BoostrapKeysSerializer
from vmware.serializers.Stage2.BoostrapKey import Stage2BootstrapKeySerializer as BoostrapKeySerializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2BootstrapKeysController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = {"data": dict()}
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="bootstrap_keys_get") or user["authDisabled"]:
                Log.actionLog("Second stage bootstrap keys list", user)

                itemData["data"]["items"] = BootstrapKey.list()
                serializer = BoostrapKeysSerializer(data=itemData)
                if serializer.is_valid():
                    data["data"] = serializer.validated_data["data"]
                    data["href"] = request.get_full_path()

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    data = {
                        "Database": "Upstream data mismatch."
                    }

                    Log.log("Upstream data incorrect: "+str(serializer.errors))
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })


    @staticmethod
    def post(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="bootstrap_key_post") or user["authDisabled"]:
                Log.actionLog("Second stage bootstrap key addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = BoostrapKeySerializer(data=request.data)
                if serializer.is_valid():
                    BootstrapKey.add(serializer.validated_data["data"])
                    httpStatus = status.HTTP_201_CREATED
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "Database": {
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
