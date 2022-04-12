from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2.TargetCommand import TargetCommand
from vmware.models.Permission.Permission import Permission

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2TargetCommandController(CustomController):
    @staticmethod
    def delete(request: Request, targetId: int, commandUid: str) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_command_delete") or user["authDisabled"]:
                Log.actionLog("Second stage target command deletion", user)

                targetCommand = TargetCommand(targetId, commandUid)
                targetCommand.delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
