from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
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
        folderMoId = ""
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="folders_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("VMFolders get", user)

                lock = Lock("vmFolders", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # If asked for, get the tree format.
                    if "related" in request.GET:
                        rList = request.GET.getlist('related')
                        if "tree" in rList:
                            formatTree = True
                    if formatTree:
                        if "folder" in request.GET:
                            folderMoIdList = request.GET.getlist('folder')
                            if folderMoIdList:
                                folderMoId = folderMoIdList[0]

                    data["data"] = VirtualMachineFolder.list(assetId, formatTree, folderMoId)
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

