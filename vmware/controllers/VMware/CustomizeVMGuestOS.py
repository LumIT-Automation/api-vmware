from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VirtualMachine import VMwareVirtualMachineSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareCustomizeVMGuestOSController(CustomController):
    @staticmethod
    def patch(request: Request, assetId: int, moId: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="vm_guestos_patch", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Virtual machine guest OS customization", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                #if serializer.is_valid():
                #    data = serializer.validated_data
                if True:
                    data = request.data["data"]
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
