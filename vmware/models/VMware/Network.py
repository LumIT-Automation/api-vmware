from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VmwareHelper import VmwareHelper
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
                hostData = VmwareHelper.vmwareObjToDict(h)
                try:
                    pgObjList = self.getHostPortGroupsObjects(h)
                    for pgObj in pgObjList:
                        if pgObj.spec.name == networkInfo["name"]:
                            hostData["vlanId"] = pgObj.spec.vlanId
                except:
                    pass

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
        try:
            self.getVMwareObject()
            return self.vmwareObj.summary

        except Exception as e:
            raise e



    def listConfiguredHostsObjects(self) -> list:
        try:
            self.getVMwareObject()
            return self.vmwareObj.host

        except Exception as e:
            raise e



    # TODO: move to Hostsystem class.
    def getHostPortGroupsObjects(self, hostRef) -> list:
        try:
            pgObjList = hostRef.config.network.portgroup
            return pgObjList

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = None) -> None:
        try:
            self._getVMwareObject(vim.Network, refresh, silent)

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
                networks.append(VmwareHelper.vmwareObjToDict(n))

            return dict({
                "items": networks
            })

        except Exception as e:
            raise e



    @staticmethod
    def listNetworksInClusterObjects(cluster: object) -> list: # (List of vim.Hostsystem)
        try:
            return cluster.network

        except Exception as e:
            raise e



    @staticmethod
    # vCenter networks pyVmomi objects list.
    def listNetworksObjects(assetId, silent: bool = None) -> list:
        netObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            netObjList = vClient.getAllObjs([vim.Network])

            return netObjList

        except Exception as e:
            raise e


