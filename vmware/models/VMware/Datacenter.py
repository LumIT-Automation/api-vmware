from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

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
            computeResourcesList = self.listComputeResourcesObjects()
            # each element of computeResourcesList is a set containing a vmware ClusterComputeResource object.
            for c in computeResourcesList:
                clusters.append(VMwareObj.vmwareObjToDict(c))

            dsList = self.listDatastoresObjects()
            # each element of dsList is a set containing a vmware Datastore object.
            for ds in dsList:
                for d in ds:
                    datastores.append(VMwareObj.vmwareObjToDict(d))

            nList = self.listNetworksObjects()
            # each element of computeResources is a set containing a vmware Network object.
            for net in nList:
                for n in net:
                    networks.append(VMwareObj.vmwareObjToDict(n))

            return dict({
                "clusters": clusters,
                "datastores": datastores,
                "networks": networks
            })

        except Exception as e:
            raise e



    def listComputeResourcesObjects(self) -> list:
        computeResources = []
        try:
            self.getVMwareObject()
            for child in self.vmwareObj.hostFolder.childEntity:
                if isinstance(child, vim.ComputeResource):
                    computeResources.append(child)
            return computeResources

        except Exception as e:
            raise e



    def listDatastoresObjects(self) -> list:
        datastores = []
        try:
            self.getVMwareObject()
            for child in self.vmwareObj.datastoreFolder.childEntity:
                if isinstance(child, vim.Datastore):
                    datastores.append({child})
            return datastores

        except Exception as e:
            raise e



    def listNetworksObjects(self) -> list:
        networks = []
        try:
            self.getVMwareObject()
            for child in self.vmwareObj.networkFolder.childEntity:
                if isinstance(child, vim.Network):
                    networks.append({child})
            return networks

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        try:
            self._getVMwareObject(vim.Datacenter, refresh, silent)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = True) -> dict:
        datacenters = []
        try:
            dcObjList = Datacenter.listDatacentersObjects(assetId, silent)

            for dc in dcObjList:
                datacenters.append(VMwareObj.vmwareObjToDict(dc))

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter datacenter pyVmomi objects list.
    def listDatacentersObjects(assetId, silent: bool = True) -> list:
        dcObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            dcObjList = vClient.getAllObjs([vim.Datacenter])

            return dcObjList

        except Exception as e:
            raise e






