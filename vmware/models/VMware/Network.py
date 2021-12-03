from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class Network(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        configuredHosts = []
        networkInfo = None
        try:
            networkInfo = self.getNetworkInfo()

            configuredHostsObjs = self.listConfiguredHostsObjects()
            for h in configuredHostsObjs:
                hostData = VMwareObj.vmwareObjToDict(h)
                pgInfo = self.getHostPortGroupsObjects(h)
                for pg in pgInfo:
                    if pg.spec.name == networkInfo["name"]:
                        hostData["vlanId"] = pg.spec.vlanId

                configuredHosts.append(hostData)

            networkInfo = self.getNetworkInfo()

            return dict({
                "configuredHosts": configuredHosts,
                "networkInfo": networkInfo
            })

        except Exception as e:
            raise e



    def getNetworkInfo(self) -> dict:
        info = dict()
        try:
            netInfo = self.getNetworkInfoObject()
            info["name"] = netInfo.name
            info["accessible"] = netInfo.accessible

            return info

        except Exception as e:
            raise e



    def getNetworkInfoObject(self) -> object:
        netInfo = None
        try:
            self.__getObject()
            netObj = self.vmwareObj
            netInfo = netObj.summary
            return netInfo

        except Exception as e:
            raise e



    def listConfiguredHostsObjects(self) -> list:
        hosts = []
        try:
            self.__getObject()
            netObj = self.vmwareObj
            hosts = netObj.host
            return hosts

        except Exception as e:
            raise e


    # TODO: move to a new Hostsystem class.
    def getHostPortGroupsObjects(self, hostRef) -> list:
        try:
            pgInfo = hostRef.config.network.portgroup
            return pgInfo

        except Exception as e:
            raise e

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter networks list.
    def list(assetId, silent: bool = None) -> dict:
        networks = []
        try:
            netObjList = Network.listNetworksObjects(assetId, silent)
            for n in netObjList:
                networks.append(VMwareObj.vmwareObjToDict(n))

            return dict({
                "items": networks
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter networks pyVmomi objects list.
    def listNetworksObjects(assetId, silent: bool = None) -> list:
        netObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            netObjList = vClient.getAllObjs([vim.Network])

            return netObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getObject(self, silent: bool = None) -> None:
        try:
            self._getObject(vim.Network, silent)

        except Exception as e:
            raise e

