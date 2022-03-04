import re
from typing import List
from pyVmomi import vim

from vmware.models.VMware.VmNetworkAdapter import VmNetworkAdapter
from vmware.models.VMware.VirtualMachineDatastore import VirtualMachineDatastore
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VirtualMachine(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = self.oVirtualMachine.name
        self.guestName: str
        self.version: str
        self.uuid: str
        self.numCpu: int
        self.numCoresPerSocket: int
        self.memoryMB: int
        self.template: bool

        self.networkDevices: List[VmNetworkAdapter] = []
        self.diskDevices: List[VirtualMachineDatastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def deploy(self, data: dict) -> str:
        from vmware.models.VMware.Cluster import Cluster
        from vmware.models.VMware.HostSystem import HostSystem
        from vmware.models.VMware.Datastore import Datastore
        from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder
        from vmware.models.VMware.CustomSpec import CustomSpec

        devsSpecs = None
        oCustomSpec = None
        host = None
        cluster = None
        checkNetworkStorageAttached = None
        try:
            # Perform some preliminary checks.
            # - "clusterMoId" and not "hostMoId" -> deploy in cluster, vmware choose the host.
            # - "clusterMoId" and "hostMoId" -> deploy in specific host of the cluster.
            # - not "clusterMoId" and "hostMoId" -> deploy in standalone host (not in a host of a cluster)
            if "clusterMoId" in data and "hostMoId" in data:
                if self.__isClusterValid(data["datacenterMoId"], data["clusterMoId"]):
                    cluster = Cluster(self.assetId, data["clusterMoId"])
                    if self.__isHostValid(data["clusterMoId"], data["hostMoId"]): # preferred host in cluster.
                        host = HostSystem(self.assetId, data["hostMoId"])
                        checkNetworkStorageAttached = host # preferred host choosed: check that datastore and network are attached to it.
            elif "clusterMoId" in data and "hostMoId" not in data:
                if self.__isClusterValid(data["datacenterMoId"], data["clusterMoId"]):
                    cluster = Cluster(self.assetId, data["clusterMoId"])
                    checkNetworkStorageAttached = cluster # check that datastore and network are attached to the cluster.
            elif "clusterMoId" not in data and "hostMoId" in data:
                if self.__isStandaloneHostValid(data["datacenterMoId"], data["hostMoId"]):  # standalone host.
                    host = HostSystem(self.assetId, data["hostMoId"])
                    checkNetworkStorageAttached = host # standalone host: check that datastore and network are attached to it.
            else:
                raise CustomException(status=400, payload={"VMware": "missing both cluster and host params."})

            # Check datastore/network connection with cluster/single host.
            if self.__isDatastoreValid(checkNetworkStorageAttached, data["datastoreMoId"]):
                if "networkId" not in data or self.__isNetworkValid(checkNetworkStorageAttached, data["networkMoId"]):  # Allow to deploy a VM without touching the network card.
                    datastore = Datastore(self.assetId, data["datastoreMoId"])
                    vmFolder = VirtualMachineFolder(self.assetId, data["vmFolderMoId"])

                    if "diskDevices" in data:
                        devsSpecs = self.buildStorageSpec(data["diskDevices"], data["datastoreMoId"])
                    if "networkDevices" in data:
                        nicsSpecs = self.buildNetworkSpec(data["networkDevices"])
                        if devsSpecs:
                            devsSpecs.extend(nicsSpecs)
                        else:
                            devsSpecs = nicsSpecs

                        # Apply the guest OS customization specifications.
                        if "guestSpec" in data and data["guestSpec"]:
                            oCustomSpec = CustomSpec(self.assetId).oCustomSpec(data["guestSpec"])

                        # Deploy
                        cloneSpec = self.buildVMCloneSpecs(oDatastore=datastore.oDatastore, devsSpecs=devsSpecs, cluster=cluster, host=host, data=data, oCustomSpec=oCustomSpec)

                        return self.clone(oVMFolder=vmFolder.oVMFolder, vmName=data["vmName"], cloneSpec=cloneSpec)

        except Exception as e:
            raise e



    def modify(self, data: dict) -> str:
        nicsSpec = None
        devsSpecs = None

        try:
            vmDatastoreMoId = self.info(related=False)["defaultDatastoreMoId"]
            if "diskDevices" in data:
                devsSpecs = self.buildStorageSpec(data["diskDevices"], vmDatastoreMoId)
                data.pop("diskDevices")
            if "networkDevices" in data:
                nicsSpec = self.buildNetworkSpec(data["networkDevices"])
                data.pop("networkDevices")
                if devsSpecs:
                    devsSpecs.extend(nicsSpec)
                else:
                    devsSpecs = nicsSpec

            modifySpec = self.buildVMConfigSpecs(data, devsSpecs)

            return self.reconfig(configSpec=modifySpec)

        except Exception as e:
            raise e



    def loadVMDatastores(self) -> None:
        try:
            for l in self.listVMDiskInfo():
                self.diskDevices.append(
                    VirtualMachineDatastore(self.assetId, l["datastore"], l["label"], l["sizeMB"], l["deviceType"])
                )
        except Exception as e:
            raise e



    def loadVMNetworks(self) -> None:
        try:
            for l in self.listVMNetworkInfo():
                self.networkDevices.append(
                    VmNetworkAdapter(self.assetId, l["network"], l["label"], l["deviceType"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True) -> dict:
        vmDisks = list()
        vmNets = list()
        defaultDatastoreMoId = ""

        try:
            config = self.oVirtualMachine.config

            if related:
                # Get virtual disks info.
                self.loadVMDatastores()
                for disk in self.diskDevices:
                    vmDisks.append(
                        disk.info()
                    )

                # Get the datastore where the vmx file is contained.
                defaultDatastoreName = re.findall('\[(.*)\]', config.files.vmPathName)[0]
                defaultDatastoreMoId = Datastore.getDatastoreMoIdByName(self.assetId, defaultDatastoreName)

                # Get network devices info.
                self.loadVMNetworks()
                for net in self.networkDevices:
                    vmNets.append(
                        net.info()
                    )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": config.name,
                "defaultDatastoreMoId": defaultDatastoreMoId,
                "guestName": config.guestFullName,
                "version": config.version,
                "uuid": config.uuid,
                "numCpu": config.hardware.numCPU,
                "numCoresPerSocket": config.hardware.numCoresPerSocket,
                "memoryMB": config.hardware.memoryMB,
                "template": config.template,
                "notes": config.annotation,

                "networkDevices": {
                    "existent": vmNets
                },
                "diskDevices": {
                    "existent": vmDisks
                }
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __isClusterValid(self, datacenterMoId: str, clusterMoId: str) -> bool:
        from vmware.models.VMware.Datacenter import Datacenter
        try:
            datacenter = Datacenter(self.assetId, datacenterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

        try:
            datacenter.loadClusters()
            for cluster in datacenter.clusters:
                if clusterMoId == cluster.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "cluster not found in this datacenter."})
        except Exception as e:
            raise e



    def __isHostValid(self, clusterMoId: str, hostMoId: str) -> bool:
        from vmware.models.VMware.Cluster import Cluster
        try:
            cluster = Cluster(self.assetId, clusterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid cluster."})

        try:
            cluster.loadHosts()
            for host in cluster.hosts:
                if hostMoId == host.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "host not found in this cluster."})
        except Exception as e:
            raise e



    def __isStandaloneHostValid(self, datacenterMoId: str, hostMoId: str) -> bool:
        from vmware.models.VMware.Datacenter import Datacenter

        try:
            datacenter = Datacenter(self.assetId, datacenterMoId)
        except Exception:
            raise CustomException(status=400, payload={"VMware": "invalid datacenter."})

        try:
            datacenter.loadHosts()
            for host in datacenter.hosts:
                if hostMoId == host.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "host not found in this datacenter."})
        except Exception as e:
            raise e



    # computeResource can be a cluster or a single host.
    def __isDatastoreValid(self, computeResource: object, datastoreMoId: str) -> bool:
        try:
            computeResource.loadDatastores()
            for datastore in computeResource.datastores:
                if datastoreMoId == datastore.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "datastore not found in this cluster."})
        except Exception as e:
            raise e



    # computeResource can be a cluster or a single host.
    def __isNetworkValid(self, computeResource: object, networkMoId: str) -> bool:
        try:
            computeResource.loadNetworks()
            for network in computeResource.networks:
                if networkMoId == network.moId:
                    return True

            raise CustomException(status=400, payload={"VMware": "network not attached to this cluster."})
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        virtualmachines = list()

        try:
            for o in Backend.oVirtualMachines(assetId):
                virtualmachine = VirtualMachine(assetId, VmwareHelper.vmwareObjToDict(o)["moId"])
                virtualmachines.append(
                    VirtualMachine._cleanup("list", virtualmachine.info(related))
                )

            return virtualmachines
        except Exception as e:
            raise e



    ####################################################################################################################
    # Protected static methods
    ####################################################################################################################

    @staticmethod
    def _cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "list":
                if not o["networkDevices"] or not o["networkDevices"]["existent"]:
                    del (o["networkDevices"])

                if not o["diskDevices"] or not o["diskDevices"]["existent"]:
                    del (o["diskDevices"])

                if not o["defaultDatastoreMoId"]:
                    del (o["defaultDatastoreMoId"])
        except Exception:
            pass

        return o
