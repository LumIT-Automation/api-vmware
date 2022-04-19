from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.helpers.SSHCommandRun import SSHCommandRun
from vmware.models.Permission.Permission import Permission

from vmware.serializers.Stage2.CommandRun import Stage2CommandRunSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2CommandRunController(CustomController):
    @staticmethod
    def put(request: Request, commandUid: str, targetId: int, pubKeyId: int = 0) -> Response:
        data = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="commandrun_put") or user["authDisabled"]:
                Log.actionLog("Second stage command run", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data["data"], error, exitStatus = SSHCommandRun(
                        commandUid=commandUid,
                        targetId=targetId,
                        userArgs=serializer.validated_data["args"],

                        pubKeyId=pubKeyId # useful only for public key management.
                    )()

                    data["href"] = request.get_full_path()
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    data = {
                        "VMware": {
                            "error": str(serializer.errors)
                        }
                    }

                    Log.actionLog("User data incorrect: "+str(data), user)
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
