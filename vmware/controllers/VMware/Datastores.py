from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Datastore import Datastore
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.Datastores import VMwareDatastoresSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareDatastoresController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        allowedData = {
            "items": []
        }
        allowedObjectsMoId = set()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if user["authDisabled"]:
                allowedObjectsMoId = {"any"}
            else:
                allowedObjectsMoId = Permission.allowedObjectsSet(groups=user["groups"], action="datastores_get", assetId=assetId)

            if allowedObjectsMoId:
                Log.actionLog("datastores list", user)

                lock = Lock("datastore", locals())
                if lock.isUnlocked():
                    lock.lock()

                    if "quick" in request.GET:
                        itemData["items"] = Datastore.listQuick(assetId)
                    else:
                        itemData["items"] = Datastore.list(assetId)

                    # Filter datastores' list basing on permissions.
                    if "any" in allowedObjectsMoId:
                        allowedData = itemData
                    else:
                        for n in itemData["items"]:
                            if n["moId"] in allowedObjectsMoId:
                                allowedData["items"].append(n)

                    serializer = Serializer(data=allowedData)
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
                        data["href"] = request.get_full_path()

                        # Check the response's ETag validity (against client request).
                        conditional = Conditional(request)
                        etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                        if etagCondition["state"] == "fresh":
                            data = None
                            httpStatus = status.HTTP_304_NOT_MODIFIED
                        else:
                            httpStatus = status.HTTP_200_OK
                    else:
                        httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                        data = {
                            "VMware": "upstream data mismatch."
                        }
                        Log.log("Upstream data incorrect: "+str(serializer.errors))
                    lock.release()
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("datastore", locals()).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
