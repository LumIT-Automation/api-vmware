from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.commands.Stage2.AddMountPoint import AddMountPoint
from vmware.models.Permission.Permission import Permission
from vmware.serializers.Stage2.AddMountPoint import Stage2AddMountPointSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2AddMountPointController(CustomController):
    @staticmethod
    def put(request: Request, targetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="add_mount_point_put") or user["authDisabled"]:
                Log.actionLog("Second stage system reboot", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    target = AddMountPoint(targetId)
                    response = target.exec(data)
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
