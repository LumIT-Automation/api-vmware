from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Node import Node
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.Nodes import VMwareNodesSerializer as NodesSerializer
from vmware.serializers.VMware.Node import VMwareNodeSerializer as NodeSerializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Conditional import Conditional
from vmware.helpers.Log import Log


class VMwareNodesController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, vmFolderName: str) -> Response:
        data = dict()
        etagCondition = { "responseEtag": "" }

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="nodes_get", assetId=assetId, vmFolderName=vmFolderName) or user["authDisabled"]:
                Log.actionLog("Nodes list", user)

                lock = Lock("node", locals())
                if lock.isUnlocked():
                    lock.lock()

                    itemData = Node.list(assetId, vmFolderName)
                    data["data"] = NodesSerializer(itemData).data["data"]
                    data["href"] = request.get_full_path()

                    # Check the response's ETag validity (against client request).
                    conditional = Conditional(request)
                    etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                    if etagCondition["state"] == "fresh":
                        data = None
                        httpStatus = status.HTTP_304_NOT_MODIFIED
                    else:
                        httpStatus = status.HTTP_200_OK

                    lock.release()
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("node", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request, assetId: int, vmFolderName: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="nodes_post", assetId=assetId, vmFolderName=vmFolderName) or user["authDisabled"]:
                Log.actionLog("Node addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = NodeSerializer(data=request.data)
                if serializer.is_valid():
                    data = serializer.validated_data["data"]
                    data["vmFolder"] = vmFolderName
                    if "state" in data:
                        data["State"] = data["state"] # curious VMware field's name.
                        del(data["state"])

                    lock = Lock("node", locals(), data["name"])
                    if lock.isUnlocked():
                        lock.lock()

                        Node.add(assetId, data)

                        httpStatus = status.HTTP_201_CREATED
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
            Lock("node", locals(), locals()["serializer"].data["data"]["name"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
