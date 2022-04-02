from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.IdentityGroup import IdentityGroup
from vmware.models.Permission.Permission import Permission
from vmware.models.Permission.VObject import VObject

from vmware.serializers.Permission.Permissions import PermissionsSerializer
from vmware.serializers.Permission.Permission import PermissionSerializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Conditional import Conditional
from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException


class PermissionsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = dict()
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroups_get") or user["authDisabled"]:
                Log.actionLog("Permissions list", user)

                itemData["items"] = Permission.rawList()
                serializer = PermissionsSerializer(data=itemData)
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
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroups_post") or user["authDisabled"]:
                Log.actionLog("Permission addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = PermissionSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    try:
                        identityGroupId = IdentityGroup(data["identity_group_identifier"]).id
                    except Exception:
                        raise CustomException(status=status.HTTP_422_UNPROCESSABLE_ENTITY, payload={"database": "Group identifier doesn't exist."})

                    Permission.add(
                        identityGroupId,
                        data["role"],
                        VObject(
                            assetId=data["object"]["id_asset"],
                            moId=data["object"]["moId"],
                            name=data["object"]["name"]
                        )
                    )

                    httpStatus = status.HTTP_201_CREATED
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
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
