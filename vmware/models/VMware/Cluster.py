from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset
from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
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
        hosts = list()
        try:
            self.__getObject()
            hosts = self.vmwareObj.host
            return hosts

        except Exception as e:
            raise e



    def listDatastores(self) -> list:
        ds = list()
        try:
            self.__getObject()
            ds = self.vmwareObj.datastore
            return ds

        except Exception as e:
            raise e



    def listNetworks(self) -> list:
        n = list()
        try:
            self.__getObject()
            n = self.vmwareObj.network
            return n

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = None) -> list:
        clustersObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            clList = vClient.getAllObjs([vim.ComputeResource])

            for cl in clList:
                clustersObjList.append(cl)

            return clustersObjList

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter datacenters list.
    def listData(assetId, silent: bool = None) -> dict:
        clusters = list()
        try:
            clustersObjList = Cluster.list(assetId, silent)
            for cl in clustersObjList:
                clusters.append(VMwareObj.vmwareObjToDict(cl))

            return dict({
                "items": clusters
            })

        except Exception as e:
            raise e




    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getObject(self, silent: bool = None) -> object:
        obj = None
        try:
            obj = self._getObject(vim.ComputeResource, silent)
            return obj

        except Exception as e:
            raise e

