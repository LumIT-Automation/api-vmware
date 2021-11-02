from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.Role import Role
from vmware.models.Permission.Permission import Permission

from vmware.serializers.Permission.Roles import IdentityRolesSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Conditional import Conditional
from vmware.helpers.Log import Log


class PermissionRolesController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = dict()
        showPrivileges = False
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_roles_get") or user["authDisabled"]:
                Log.actionLog("Roles list", user)

                # If asked for, get related privileges.
                if "related" in request.GET:
                    rList = request.GET.getlist('related')
                    if "privileges" in rList:
                        showPrivileges = True

                itemData["data"] = Role.list(showPrivileges)
                data["data"] = Serializer(itemData).data["data"]
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
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
