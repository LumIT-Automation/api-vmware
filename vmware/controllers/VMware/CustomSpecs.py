from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.CustomSpecManager import CustomSpecManager
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.CustomSpecs import VMwareCustomizationSpecsSerializer as Serializer, VMwareCustomizationSpecCloneSerializer as CloneSerializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareCustomSpecsController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_specs_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machines customization specifications list", user)

                lock = Lock("custom_specs", locals())
                if lock.isUnlocked():
                    lock.lock()

                    itemData["data"] = CustomSpecManager.list(assetId)
                    serializer = Serializer(data=itemData)
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data["data"]
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
                            "VMware": "Upstream data mismatch."
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
            Lock("custom_specs", locals()).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request, assetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_specs_post") or user["authDisabled"]:
                Log.actionLog("Clone virtual machines customization specification", user)
                Log.actionLog("User data: " + str(request.data), user)

                serializer = CloneSerializer(data=request.data)
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("custom_specs", locals(), data["data"]["sourceSpec"])
                    if lock.isUnlocked():
                        lock.lock()
                        CustomSpecManager.clone(assetId, serializer.validated_data["data"]["sourceSpec"], serializer.validated_data["data"]["newSpec"])

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
                    Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            if "serializer" in locals():
                Lock("custom_specs", locals(), locals()["serializer"].data["data"]["sourceSpec"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

