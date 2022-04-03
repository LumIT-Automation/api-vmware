from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.CustomSpec import CustomSpec
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.CustomSpec import VMwareCustomizationSpecSerializer as Serializer, \
    VMwareCustomizationSpecCloneSerializer as CloneSerializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareCustomSpecController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, specName: str) -> Response:
        data = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_spec_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machine customization specification details", user)

                lock = Lock("custom_spec", locals(), specName)
                if lock.isUnlocked():
                    lock.lock()

                    itemData = CustomSpec(assetId, specName).info()
                    serializer = Serializer(data=itemData)
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
            if "specName" in locals():
                Lock("custom_spec", locals(), locals()["specName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def delete(request: Request, assetId: int, specName: str) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_spec_delete", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machine customization specification deletion", user)

                lock = Lock("custom_spec", locals(), specName)
                if lock.isUnlocked():
                    lock.lock()

                    CustomSpec(assetId, specName).delete()
                    httpStatus = status.HTTP_200_OK
                    lock.release()
                else:
                    httpStatus = status.HTTP_423_LOCKED
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "specName" in locals():
                Lock("custom_spec", locals(), locals()["specName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, assetId: int, specName: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)
        data = dict()

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_spec_patch", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machine customization specification edit", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data
                    lock = Lock("custom_spec", locals(), specName)
                    if lock.isUnlocked():
                        lock.lock()

                        CustomSpec(assetId, specName).modify(data)
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
            if "specName" in locals():
                Lock("custom_spec", locals(), locals()["specName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def post(request: Request, assetId: int, specName: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="custom_specs_post") or user["authDisabled"]:
                Log.actionLog("Clone virtual machines customization specification", user)
                Log.actionLog("User data: " + str(request.data), user)

                serializer = CloneSerializer(data=request.data["data"])
                if serializer.is_valid():
                    lock = Lock("custom_spec", locals(), specName)
                    if lock.isUnlocked():
                        lock.lock()
                        CustomSpec(assetId, specName).clone(serializer.validated_data["destination"])

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
            if "specName" in locals():
                Lock("custom_spec", locals(), locals()["specName"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
