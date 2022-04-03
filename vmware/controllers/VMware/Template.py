from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Template import VirtualMachineTemplate
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VirtualMachine import VMwareVirtualMachineSerializer as Serializer
from vmware.serializers.VMware.Template import VMwareDeployTemplateSerializer as DeploySerializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVirtualMachineTemplateController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="template_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("VirtualMachineTemplate info", user)

                lock = Lock("template", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    template = VirtualMachineTemplate(assetId, moId)
                    itemData = template.info()
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
            if "moId" in locals():
                Lock("template", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    # @todo: move away.
    @staticmethod
    def post(request: Request, assetId: int, moId: str) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="template_post", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Deploy new virtual machines from template", user)
                Log.actionLog("User data: " + str(request.data), user)

                serializer = DeploySerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    lock = Lock("template", locals(), moId)
                    if lock.isUnlocked():
                        lock.lock()

                        template = VirtualMachineTemplate(assetId, moId)
                        response["data"] = template.deploy(serializer.validated_data)
                        httpStatus = status.HTTP_202_ACCEPTED
                        lock.release()
                        Log.actionLog("Deploy task moId: "+str(response["data"]), user)
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
            if "moId" in locals():
                Lock("template", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



