from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.commands.Stage2.TargetAddFinalPubKey import TargetAddFinalPubKey
from vmware.models.Permission.Permission import Permission

from vmware.controllers.CustomController import CustomController
from vmware.serializers.Stage2.TargetAddFinalPubKeys import Stage2TargetAddFinalPubKeysSerializer as Serializer

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class Stage2TargetAddFinalPubKeyController(CustomController):
    @staticmethod
    def put(request: Request, targetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="add_final_pubkeys_put") or user["authDisabled"]:
                Log.actionLog("Second stage: add final pub keys", user)
                Log.actionLog("User data: " + str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    # Have a check before.
                    for k in data["keyIds"]:
                        try:
                            TargetAddFinalPubKey(targetId, k)
                        except Exception:
                            raise CustomException(status=400, payload={"VMware": "Some invalid key id passed."})

                    # Finally execute.
                    for k in data["keyIds"]:
                        target = TargetAddFinalPubKey(targetId, k)
                        target.exec()

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "VMware": {
                            "error": str(serializer.errors)
                        }
                    }

                    Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
