from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Stage2 import Target
from vmware.models.Permission.Permission import Permission
#from vmware.serializers.VMware.Asset.Asset import VMwareAssetSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Log import Log


class Stage2TargetController(CustomController):
    @staticmethod
    def delete(request: Request, targetId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_delete") or user["authDisabled"]:
                Log.actionLog("Second stage target deletion", user)

                vmware = Target(targetId)
                vmware.delete()

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
    def patch(request: Request, targetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="target_patch") or user["authDisabled"]:
                Log.actionLog("Second stager target modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                if True:
                    data = request.data
                #serializer = Serializer(data=request.data, partial=True)
                #if serializer.is_valid():
                #    data = serializer.validated_data["data"]

                    vmware = Target(targetId)
                    vmware.modify(data)

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

