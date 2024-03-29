from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VMGuestOS import VMwareVMGuestOSSerializer as Serializer
from vmware.serializers.VMware.VMGuestOS import VMwareVMGuestOSCustomizeSerializer as CustomizeSerializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVirtualMachineGuestOSController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="virtualmachine_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("VirtualMachine guest info", user)

                lock = Lock("virtualmachine", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    virtualmachine = VirtualMachine(assetId, moId)
                    itemData = virtualmachine.guestInfo()
                    serializer = Serializer(data=itemData)
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
                    #if True:
                    #    data["data"] = itemData
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
                Lock("virtualmachine", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def patch(request: Request, assetId: int, moId: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="vm_guestos_patch", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machine guest OS customization", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = CustomizeSerializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("virtualmachine", locals(), moId)
                    if lock.isUnlocked():
                        lock.lock()

                        vm = VirtualMachine(assetId, moId)
                        vm.customizeGuestOS(data)
                        httpStatus = status.HTTP_202_ACCEPTED
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
            if "moId" in locals():
                Lock("virtualmachine", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
