from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.Permission.IdentityGroup import IdentityGroup
from vmware.models.Permission.Role import Role
from vmware.models.Permission.Permission import Permission
from vmware.models.Permission.VObject import VObject

from vmware.serializers.Permission.Permission import PermissionSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class PermissionController(CustomController):
    @staticmethod
    def delete(request: Request, permissionId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_delete") or user["authDisabled"]:
                Log.actionLog("Permission deletion", user)

                p = Permission(permissionId)
                p.delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, permissionId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_patch") or user["authDisabled"]:
                Log.actionLog("Permission modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    group = data["identity_group_identifier"]
                    role = data["role"]

                    oMoId = data["object"]["moId"]
                    oName = data["object"]["name"]
                    oAssetId = data["object"]["id_asset"]

                    # Get existent or new object.
                    try:
                        vmo = VObject(assetId=oAssetId, moId=oMoId)
                    except CustomException as e:
                        if e.status == 404:
                            try:
                                # If object does not exist, create it (on Permissions database).
                                vmo = VObject(
                                    id=VObject.add(
                                        moId=oMoId,
                                        assetId=oAssetId,
                                        objectName=oName,
                                        role=role
                                    )
                                )
                            except Exception:
                                raise e
                        else:
                            raise e

                    Permission(permissionId).modify(
                        identityGroup=IdentityGroup(identityGroupIdentifier=group),
                        role=Role(role=role),
                        vmwareObject=vmo
                    )

                    httpStatus = status.HTTP_200_OK
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
