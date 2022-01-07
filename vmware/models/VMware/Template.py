from pyVmomi import vim, vmodl

from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.VMFolder import VMFolder

from vmware.helpers.Log import Log
from vmware.helpers.VMwareObj import VMwareObj

from vmware.helpers.Exception import CustomException



class VirtualMachineTemplate(VirtualMachine):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        if not self.__isVmTemplate():
            raise CustomException(status=400, payload={"VMware": "this object is not a virtual machine template."})

        info = super().info()
        return info



    # https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/clone_vm.py
    def waitForTask(self, task):
        """ wait for a vCenter task to finish """
        task_done = False
        while not task_done:
            if task.info.state == 'success':
                return task.info.result

            if task.info.state == 'error':
                print("there was an error")
                print(task.info.error)
                task_done = True



    def deployVM(self, data: dict) -> bool:
        datacenter = Datacenter(self.assetId, data["datacenterId"])

        dcClusterObjList = datacenter.listComputeResourcesObjects()
        # each element of dcClusterObjList is a set containing a vmware ClusterComputeResource object.
        dcClusterIdList = []
        for cSet in dcClusterObjList:
            for c in cSet:
                dcClusterIdList.append(VMwareObj.vmwareObjToDict(c)["moId"]) # Build a list of the moIds of the clusters found in this datacenter.

        if data["clusterId"] in dcClusterIdList:
            cluster = Cluster(self.assetId, data["clusterId"])
            cluster.getVMwareObject()
            clusterObj = cluster.vmwareObj # Got the right VMware cluster object.
        else:
            raise CustomException(status=400, payload={"VMware": "clusterId not found in this datacenter."})

        cluDatastoreObjList = cluster.listDatastoresObjects()
        cluDatastoreIdList = []
        for d in cluDatastoreObjList:
            cluDatastoreIdList.append(VMwareObj.vmwareObjToDict(d)["moId"]) # Build a list of the moIds of the datastores found attached to this cluster.
        if data["datastoreId"] in cluDatastoreIdList:
            datastore = Datastore(self.assetId, data["datastoreId"])
            datastore.getVMwareObject()
            datastoreObj = datastore.vmwareObj # Got the right VMware datastore object.
        else:
            raise CustomException(status=400, payload={"VMware": "datastoreId not found attached to this cluster."})

        cluNetworkObjList = cluster.listNetworksObjects()
        cluNetworkIdList = []
        for n in cluNetworkObjList:
            cluNetworkIdList.append(VMwareObj.vmwareObjToDict(n)["moId"])
        if data["networkId"] in cluNetworkIdList:
            network = Network(self.assetId, data["networkId"])
            network.getVMwareObject()
            networkObj = network.vmwareObj
        else:
            raise CustomException(status=400, payload={"VMware": "networkId not found attached to this cluster."})

        vmFolder = VMFolder(self.assetId, data["vmFolderId"])
        vmFolder.getVMwareObject()
        vmFolderObj = vmFolder.vmwareObj

        # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
        relocateSpec = vim.vm.RelocateSpec()
        relocateSpec.datastore = datastoreObj
        relocateSpec.pool = clusterObj.resourcePool # The resource pool associated to this cluster.

        # VirtualMachineCloneSpec(vim.vm.CloneSpec): virtual machine specifications.
        cloneSpec = vim.vm.CloneSpec()
        cloneSpec.location = relocateSpec
        cloneSpec.powerOn = data["powerOn"]

        self.getVMwareObject()
        templateObj = self.vmwareObj
        # Deploy
        task = templateObj.Clone(folder=vmFolderObj, name=data["vmName"], spec=cloneSpec)
        self.waitForTask(task)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = True) -> dict:
        tList = []
        try:
            tObjList = VirtualMachineTemplate.listTemplatesOnlyObjects(assetId, silent)

            for t in tObjList:
                tList.append(VMwareObj.vmwareObjToDict(t))

            return dict({
                "items": tList
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter templates (not regular virtual machines) pyVmomi objects list.
    def listTemplatesOnlyObjects(assetId, silent: bool = True) -> list:
        tObjList = list()
        try:
            objList = VirtualMachine.listVirtualMachinesObjects(assetId, silent)
            for obj in objList:
                if obj.config.template:
                    tObjList.append(obj)

            return tObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __isVmTemplate(self):
        config = self.getVirtualMachineConfigObject()
        return config.template