from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VMFolder import VMFolder
from vmware.models.Permission.Permission import Permission

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVMFoldersController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        formatTree = False
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="folders_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("VMFolders tree", user)

                lock = Lock("vmFolders", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # If asked for, get related privileges.
                    if "related" in request.GET:
                        rList = request.GET.getlist('related')
                        if "tree" in rList:
                            formatTree = True

                    data["data"] = VMFolder.list(assetId, formatTree)
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

