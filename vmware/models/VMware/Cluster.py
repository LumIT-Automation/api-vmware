from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VMwareObj import VMwareObj
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
            hosts = self.listHosts()
            datastores = self.listDatastores()
            networks = self.listNetworks()

            for h in hosts:
                o["hosts"].append(VMwareObj.vmwareObjToDict(h))

            for d in datastores:
                o["datastores"].append(VMwareObj.vmwareObjToDict(d))

            for n in networks:
                o["networks"].append(VMwareObj.vmwareObjToDict(n))

            return o

        except Exception as e:
            raise e



    def listHosts(self) -> list:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.host

        except Exception as e:
            raise e



    def listDatastores(self) -> list:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.datastore

        except Exception as e:
            raise e



    def listNetworks(self) -> list:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.network

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId, silent: bool = None) -> dict:
        clusters = list()
        try:
            clustersObjList = Cluster.listClustersObjects(assetId, silent)
            for cl in clustersObjList:
                clusters.append(VMwareObj.vmwareObjToDict(cl))

            return dict({
                "items": clusters
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter cluster pyVmomi objects list.
    def listClustersObjects(assetId, silent: bool = None) -> list:
        clustersObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            clList = vClient.getAllObjs([vim.ComputeResource])

            for cl in clList:
                clustersObjList.append(cl)

            return clustersObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getVMwareObject(self, refresh: bool = False, silent: bool = None) -> object:
        obj = None
        try:
            self._getVMwareObject(vim.ComputeResource, refresh, silent)

        except Exception as e:
            raise e

