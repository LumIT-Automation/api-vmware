from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset
from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class Datacenter(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        clusters = []
        datastores = []
        networks = []
        try:
            computeResourcesList = self.listComputeResources()
            # each element of computeResourcesList is a set containing a vmware ClusterComputeResource object.
            for cr in computeResourcesList:
                for c in cr:
                    clusters.append(VMwareObj.vmwareObjToDict(c))

            dsList = self.listDatastores()
            # each element of dsList is a set containing a vmware Datastore object.
            for ds in dsList:
                for d in ds:
                    datastores.append(VMwareObj.vmwareObjToDict(d))

            nList = self.listNetworks()
            # each element of computeResources is a set containing a vmware Network object.
            for net in nList:
                for n in net:
                    networks.append(VMwareObj.vmwareObjToDict(n))

            Log.log(datastores, '_')

            return dict({
                "clusters": clusters,
                "datastores": datastores,
                "networks": networks
            })

        except Exception as e:
            raise e



    def listComputeResources(self) -> list:
        computeResources = []
        try:
            self.__getObject()
            dcObj = self.vmwareObj
            for child in dcObj.hostFolder.childEntity:
                if isinstance(child, vim.ComputeResource):
                    computeResources.append({child})
            return computeResources

        except Exception as e:
            raise e



    def listDatastores(self) -> list:
        datastores = []
        try:
            self.__getObject()
            dcObj = self.vmwareObj
            for child in dcObj.datastoreFolder.childEntity:
                if isinstance(child, vim.Datastore):
                    datastores.append({child})
            return datastores

        except Exception as e:
            raise e



    def listNetworks(self) -> list:
        networks = []
        try:
            self.__getObject()
            dcObj = self.vmwareObj
            for child in dcObj.networkFolder.childEntity:
                if isinstance(child, vim.Network):
                    networks.append({child})
            return networks

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = None) -> list:
        dcObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            dcObjList = vClient.getAllObjs([vim.Datacenter])

            return dcObjList

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter datacenters list.
    def listData(assetId, silent: bool = None) -> dict:
        datacenters = []
        try:
            dcObjList = Datacenter.list(assetId, silent)

            for dc in dcObjList:
                datacenters.append(VMwareObj.vmwareObjToDict(dc))

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getObject(self, silent: bool = None) -> None:
        try:
            self._getObject(vim.Datacenter, silent)

        except Exception as e:
            raise e

