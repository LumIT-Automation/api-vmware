from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VirtualMachineFolders import VMwareVirtualMachinesFolderSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVMFoldersController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        allowedData = {
            "items": []
        }
        allowedObjectsMoId = []
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if user["authDisabled"]:
                allowedObjectsMoId = ["any"]
            else:
                allowedObjectsMoId = Permission.listAllowedObjects(groups=user["groups"], action="folders_get", assetId=assetId)

            if allowedObjectsMoId:
                Log.actionLog("VMFolders get", user)

                lock = Lock("vmFolders", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # Filter folders' list basing on permissions.
                    itemData["items"] = VirtualMachineFolder.list(assetId)
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
            Lock("vmFolders", locals()).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

