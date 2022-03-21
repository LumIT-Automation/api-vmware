from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.commands.Stage2.TargetDelBootStrapKey import TargetDelBootstrapKey
from vmware.models.Permission.Permission import Permission
from vmware.serializers.Stage2.Target import Stage2TargetSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2TargetDelBootstrapKeyController(CustomController):
    @staticmethod
    def delete(request: Request, targetId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_bootstrap_key_delete") or user["authDisabled"]:
                Log.actionLog("Second stage target deletion", user)

                target = TargetDelBootstrapKey(targetId)
                target.exec()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

