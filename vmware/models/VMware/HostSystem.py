from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class HostSystem(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        datastores = networks = []
        o = {
            "datastores": [],
            "networks": []
        }

        try:
            datastores = self.listDatastoresObjects()
            networks = self.listNetworksObjects()

            for d in datastores:
                o["datastores"].append(VmwareHelper.vmwareObjToDict(d))

            # Add also the vlanId information.
            for n in networks:
                net = VmwareHelper.vmwareObjToDict(n)
                pgObj = self.getHostPortGroupSpec(net["name"])
                if pgObj and hasattr(pgObj, 'spec'):    # This works only for standard vSwitches.
                    net["vlanId"] = pgObj.spec.vlanId
                    o["networks"].append(net)

            return o

        except Exception as e:
            raise e



    def listDatastoresObjects(self) -> list:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.datastore

        except Exception as e:
            raise e



    def listNetworksObjects(self) -> list:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.network

        except Exception as e:
            raise e



    # Host port group specifications. This is a vmware property, not a Managed Object, so it haven't a moId.
    def getHostPortGroupSpec(self, name) -> object:
        try:
            self.__getVMwareObject()
            pgList = self.vmwareObj.config.network.portgroup
            for pg in pgList:
                if pg.spec.name == name:
                     return pg

        except Exception as e:
            raise e

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listHostsInClusterObjects(cluster: object) -> list: # (List of vim.Hostsystem)
        try:
            return cluster.host

        except Exception as e:
            raise e



    @staticmethod
    # vCenter cluster pyVmomi objects list.
    def list(assetId, silent: bool = True) -> dict:
        hosts = list()
        try:
            hostsObjList = HostSystem.listHostsObjects(assetId, silent)
            for h in hostsObjList:
                hosts.append(VmwareHelper.vmwareObjToDict(h))

            return dict({
                "items": hosts
            })

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter hosts list.
    def listHostsObjects(assetId, silent: bool = True) -> list:
        hostsObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetAndGetContentStatic(assetId, silent)
            hList = vClient.getAllObjs([vim.ComputeResource])

            for h in hList:
                hostsObjList.extend(h.host)

            return hostsObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        if not self.vmwareObj or refresh:
            try:
                vClient = self.connectToAssetAndGetContent(silent)
                objList = vClient.getAllObjs([vim.ComputeResource])
                for obj in objList:
                    if obj._GetMoId() == self.moId:  # Standalone host.
                        self.vmwareObj = obj
                        break
                    if hasattr(obj, 'host'):  # If this is a cluster, loop into it.
                        for h in obj.host:
                            if h._GetMoId() == self.moId:  # In cluster host.
                                self.vmwareObj = h
                                break

            except Exception as e:
                raise e
        else:
            pass
