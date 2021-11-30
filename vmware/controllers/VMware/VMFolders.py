from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VMFolder import VMFolder
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.VMFolders import VMwareVMFoldersSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVMFoldersController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        # allowedData = {
        data = {
            "data": {
                "items": []
            }
        }
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="vmFolders_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("VMFolders tree", user)

                lock = Lock("vmFolders", locals())
                if lock.isUnlocked():
                    lock.lock()

                    #vmFolder = VMFolder(assetId)
                    itemData = VMFolder.folderTree(assetId)

                    # Filter vmFolders' list basing on permissions.
                    # For any result, check if the user has got at least a pools_get permission on the vmFolder.
                    #for p in itemData["data"]["items"]:
                    #    if Permission.hasUserPermission(groups=user["groups"], action="pools_get", assetId=assetId, vmFolderName=str(p["fullPath"])) or user["authDisabled"]:
                    #        allowedData["data"]["items"].append(p)

                    #data["data"] = Serializer(allowedData).data["data"]
                    data["data"]["items"] = itemData
                    data["href"] = request.get_full_path()

                    httpStatus = status.HTTP_200_OK
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

