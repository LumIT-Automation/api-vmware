from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2.TargetCommand import TargetCommand
from vmware.models.Permission.Permission import Permission

from vmware.serializers.Stage2.TargetCommands import Stage2TargetCommandsSerializer as CommandsSerializer
from vmware.serializers.Stage2.TargetCommand import Stage2TargetCommandSerializer as CommandSerializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2TargetCommandsController(CustomController):
    @staticmethod
    def get(request: Request, targetId: int) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_commands_get") or user["authDisabled"]:
                Log.actionLog("Second stage commands per target", user)

                itemData["items"] = TargetCommand.listTargetCommands(targetId)
                serializer = CommandsSerializer(data=itemData)
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
    def post(request: Request, targetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_commands_post") or user["authDisabled"]:
                Log.actionLog("Second stage target commands addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = CommandSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    data["id_target"] = targetId
                    TargetCommand.add(data)

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
