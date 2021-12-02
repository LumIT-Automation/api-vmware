from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.Datacenters import VMwareDatacentersSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Conditional import Conditional

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log



class VMwareDatacenterController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str) -> Response:
        data = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="datacenter_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Datacenter clusters", user)

                lock = Lock("Datacenter", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    dc = Datacenter(assetId, moId)

                    data["data"] = dc.info()
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
            Lock("datacenter", locals(), locals()["moId"]).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
