from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Node import Node
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.Node import VMwareNodeSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareNodeController(CustomController):
    @staticmethod
    def delete(request: Request, assetId: int, vmFolderName: str, nodeName: str) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="node_delete", assetId=assetId, vmFolderName=vmFolderName) or user["authDisabled"]:
                Log.actionLog("Node deletion", user)

                lock = Lock("node", locals(), nodeName)
                if lock.isUnlocked():
                    lock.lock()

                    node = Node(assetId, vmFolderName, nodeName)
                    node.delete()

                    httpStatus = status.HTTP_200_OK
                    lock.release()
                else:
                    httpStatus = status.HTTP_423_LOCKED
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("node", locals(), locals()["nodeName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, assetId: int, vmFolderName: str, nodeName: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="node_patch", assetId=assetId, vmFolderName=vmFolderName) or user["authDisabled"]:
                Log.actionLog("Node modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data, partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data["data"]

                    lock = Lock("node", locals(), nodeName)
                    if lock.isUnlocked():
                        lock.lock()

                        node = Node(assetId, vmFolderName, nodeName)
                        node.modify(data)

                        httpStatus = status.HTTP_200_OK
                        lock.release()
                    else:
                        httpStatus = status.HTTP_423_LOCKED
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
            Lock("node", locals(), locals()["nodeName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
