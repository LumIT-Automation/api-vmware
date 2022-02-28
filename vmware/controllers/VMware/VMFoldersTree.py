from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
from vmware.models.Permission.Permission import Permission

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareVMFoldersTreeController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        allowedData = {
            "items": []
        }
        allowedObjectsMoId = []
        folderMoIdList = []
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if user["authDisabled"]:
                allowedObjectsMoId = ["any"]
            else:
                allowedObjectsMoId = Permission.listAllowedObjects(groups=user["groups"], action="folders_tree_get", assetId=assetId)

            if allowedObjectsMoId:
                Log.actionLog("VMFolders tree get", user)

                lock = Lock("vmFolders", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # If "folder" params are passed -> answer with the subtrees of the requested folders.
                    # If not "folder" param (empty folderMoIdList) -> answer with the full tree.
                    if "folder" in request.GET:
                        folderMoIdList = request.GET.getlist('folder')

                    # Filter folders' tree basing on permissions.
                    # "any" in allowedObjectsMoId:
                    #   - full tree without "folder" params (empty folderMoIdList).
                    #   - subtree with "folder" params (using folderMoIdList populated by the request).
                    # Not 'any" in allowedObjectsMoId:
                    #   - full tree request: make a subtree response with the folders in allowedObjectsMoId.
                    #   - subtree request: subtract from folderMoIdList the items not in allowedObjectsMoId.
                    if "any" not in allowedObjectsMoId:
                        if not folderMoIdList:
                            folderMoIdList = allowedObjectsMoId
                        else:
                            for moId in folderMoIdList:
                                if moId not in allowedObjectsMoId:
                                    folderMoIdList.remove(moId)

                    itemData["items"] = VirtualMachineFolder.foldersTree(assetId, folderMoIdList)
                    # The result is the whole tree or a list of subtrees.
                    # In the second case, the possible overlapping data should be removed:
                    # if a parent folders is also child of another subtree, it means that there is a subtree of another subtree: drop it.
                    if folderMoIdList:
                        treeLists = dict()
                        for tree in itemData["items"]:
                            treeLists[ tree["moId"] ] = VirtualMachineFolder.treeToList(tree["folders"]) # Convert the trees to plain lists. Order doesn't matter.

                        for parent in treeLists.keys():
                            for subTree in treeLists.values():
                                if parent in subTree: # The moId of a parent folder was found in another subtree.
                                    for item in itemData["items"]:
                                        if item["moId"] == parent: # Get the index of the element and remove it.
                                            index = itemData["items"].index(item)
                                            itemData["items"].pop(index)


                    #serializer = Serializer(data=allowedData)
                    #if serializer.is_valid():
                    #    data["data"] = serializer.validated_data
                    if True:
                        data["data"] = itemData
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
                        Log.log("Upstream data incorrect: " + str(serializer.errors))
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




