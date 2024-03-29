from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Network import Network
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.FindIp import VMwareFindIpSerializer as Serializer

from vmware.controllers.CustomController import CustomController

from vmware.helpers.Conditional import Conditional
from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareNetworkFindIpController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str, ipAddress: str) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="network_get", assetId=assetId, moId=moId) or user["authDisabled"]:
                if "checkNetworksWithSameVlanIds" in request.GET:
                    checkNetworksWithSameVlanIds = True
                else:
                    checkNetworksWithSameVlanIds = False
                Log.actionLog("Network: find ip: "+ipAddress+", checkNetworksWithSameVlanIds = "+str(checkNetworksWithSameVlanIds), user)

                lock = Lock("network", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    itemData["items"] = Network(assetId, moId).findVMsWithThisIpAddress(ipAddress=ipAddress, checkNetworksWithSameVlanIds=checkNetworksWithSameVlanIds)
                    serializer = Serializer(data=itemData)
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
                        data["href"] = request.get_full_path()

                        # Check the response's ETag validity (against client request).
                        conditional = Conditional(request)
                        etagCondition = conditional.responseEtagFreshnessAgainstRequest(str(data["data"]))
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
                Lock("network", locals(), locals()["moId"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
