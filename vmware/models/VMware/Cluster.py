from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj
from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class Cluster(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        hosts = datastores = networks = []
        o = {
            "hosts": [],
            "datastores": [],
            "networks": []
        }

        try:
            hosts = self.listHostsObjects()
            datastores = self.listDatastoresObjects()
            networks = self.listNetworksObjects()

            for h in hosts:
                o["hosts"].append(VmwareHelper.vmwareObjToDict(h))

            for d in datastores:
                o["datastores"].append(VmwareHelper.vmwareObjToDict(d))

            for n in networks:
                o["networks"].append(VmwareHelper.vmwareObjToDict(n))

            return o

        except Exception as e:
            raise e



    def listHostsObjects(self) -> list: # (List of vim.Hostsystem)
        try:
            self.getVMwareObject()
            return HostSystem.listHostsInClusterObjects(self.vmwareObj)

        except Exception as e:
            raise e



    def listDatastoresObjects(self) -> list:
        try:
            self.getVMwareObject()
            return Datastore.listDatastoresInClusterObjects(self.vmwareObj)

        except Exception as e:
            raise e



    def listNetworksObjects(self) -> list:
        try:
            self.getVMwareObject()
            return Network.listNetworksInClusterObjects(self.vmwareObj)

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = True) -> object:
        obj = None
        try:
            self._getVMwareObject(vim.ComputeResource, refresh, silent)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId, silent: bool = True) -> dict:
        clusters = list()
        try:
            clustersObjList = Cluster.listClustersObjects(assetId, silent)
            for cl in clustersObjList:
                clusters.append(VmwareHelper.vmwareObjToDict(cl))

            return dict({
                "items": clusters
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter cluster pyVmomi objects list.
    def listClustersObjects(assetId, silent: bool = True) -> list:
        clustersObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            clList = vClient.getAllObjs([vim.ComputeResource])

            for cl in clList:
                clustersObjList.append(cl)

            return clustersObjList

        except Exception as e:
            raise e





