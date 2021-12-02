from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Cluster import Cluster
from vmware.models.Permission.Permission import Permission

from vmware.serializers.VMware.Datacenters import VMwareDatacentersSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Conditional import Conditional

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log



class VMwareClusterController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, moId: str) -> Response:
        data = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="cluster_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Get cluster info", user)

                lock = Lock("cluster", locals(), moId)
                if lock.isUnlocked():
                    lock.lock()

                    cl = Cluster(assetId, moId)

                    data["data"] = cl.info()
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
            Lock("cluster", locals(), locals()["moId"]).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
