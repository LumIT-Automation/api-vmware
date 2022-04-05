from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2.FinalPubKey import FinalPubKey
from vmware.models.Permission.Permission import Permission

from vmware.serializers.Stage2.FinalPubKeys import Stage2FinalPubKeysSerializer as FinalPubKeysSerializer
from vmware.serializers.Stage2.FinalPubKey import Stage2FinalPubKeySerializer as FinalPubKeySerializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2FinalPubKeysController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="final_pub_keys_get") or user["authDisabled"]:
                Log.actionLog("Second stage final public keys list", user)

                itemData["items"] = FinalPubKey.list()
                serializer = FinalPubKeysSerializer(data=itemData)
                if serializer.is_valid():
                    data["data"] = serializer.validated_data
                    data["href"] = request.get_full_path()

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    data = {
                        "VMware": "upstream data mismatch."
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
            if Permission.hasUserPermission(groups=user["groups"], action="final_pub_key_post") or user["authDisabled"]:
                Log.actionLog(" Second stage final pub key addition", user)
                Log.actionLog(" User data (comment only): "+str(request.data["data"]["comment"]), user)

                serializer = FinalPubKeySerializer(data=request.data["data"])
                if serializer.is_valid():
                    FinalPubKey.add(serializer.validated_data)
                    httpStatus = status.HTTP_201_CREATED
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
