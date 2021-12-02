from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from vmware.models.VMware.Cluster import Cluster
from vmware.models.Permission.Permission import Permission

#from vmware.serializers.VMware.Datacenters import VMwareDatacentersSerializer as Serializer

from vmware.controllers.CustomController import CustomController
from vmware.helpers.Conditional import Conditional

from vmware.helpers.Lock import Lock
from vmware.helpers.Log import Log


class VMwareClustersController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)
        etagCondition = {"responseEtag": ""}

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="clusters_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Clusters list", user)

                lock = Lock("clusters", locals())
                if lock.isUnlocked():
                    lock.lock()

                    data["data"] = Cluster.listData(assetId)

                    #  serializer = Serializer(data=itemData)
                    if True:
                    #if serializer.is_valid():
                    #    data["data"] = serializer.validated_data["data"]
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
            Lock("datacenters", locals()).release()
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
