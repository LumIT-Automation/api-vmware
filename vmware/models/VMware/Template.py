from pyVmomi import vim, vmodl

from vmware.models.VMware.VirtualMachine import VirtualMachine
from vmware.models.VMware.Datacenter import Datacenter
from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.VMFolder import VMFolder

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMwareObj import VMwareObj

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



    def cloneVM(self, vmName, datacenterId, clusterId, datastoreId, networkId, vmFolderId, powerOn=False):
        datacenter = Datacenter(self.assetId, datacenterId)

        dcClusterObjList = datacenter.listComputeResourcesObjects()
        dcClusterList = []
        for c in dcClusterObjList:
            dcClusterList.append(VMwareObj.vmwareObjToDict(c))

        if {"moId": clusterId} in dcClusterList:
            cluster = Cluster(self.assetId, clusterId)
            cluster.getVMwareObject()
            clusterObj = cluster.vmwareObj
        else:
            raise CustomException(status=400, payload={"VMware": "clusterId not found in this datacenter."})

        cluDatastoreObjList = cluster.listDatastoresObjects()
        cluDatastoreList = []
        for d in cluDatastoreObjList:
            cluDatastoreList.append(VMwareObj.vmwareObjToDict(d))
        if {"moId": datastoreId} in cluDatastoreList:
            datastore = Datastore(self.assetId, datastoreId)
            datastore.getVMwareObject()
            datastoreObj = datastore.vmwareObj
        else:
            raise CustomException(status=400, payload={"VMware": "datastoreId not found attached to this cluster."})

        cluNetworkObjList = cluster.listNetworksObjects()
        cluNetworkList = []
        for n in cluNetworkObjList:
            cluNetworkList.append(VMwareObj.vmwareObjToDict(n))
        if {moId: networkId} in cluNetworkList:
            network = Network(self.assetId, networkId)
            network.getVMwareObject()
            networkObj = network.vmwareObj
        else:
            raise CustomException(status=400, payload={"VMware": "networkId not found attached to this cluster."})

        vmFolder = VMFolder(self.assetId, vmFolderId)
        vmFolder.getVMwareObject()
        vmFolderObj = vmFolder.vmwareObj

        # VirtualMachineRelocateSpec(vim.vm.RelocateSpec): where put the new virtual machine.
        relocateSpec = vim.vm.RelocateSpec()
        relocateSpec.datastore = datastoreObj
        relocateSpec.pool = clusterObj

        # VirtualMachineCloneSpec(vim.vm.CloneSpec): virtual machine specifications.
        cloneSpec = vim.vm.CloneSpec()
        cloneSpec.location = relocateSpec
        cloneSpec.powerOn = powerOn

        self.getVMwareObject()
        templateObj = self.vmwareObj
        # Deploy
        task = templateObj.Clone(folder=vmFolderObj, name=vmName, spec=cloneSpec)
        self.waitForTask(task)



    def deployNewVm(self):
"""
        if template:
            cloneVm(
                content, template, args.vm_name, args.datacenter_name, args.vm_folder,
                args.datastore_name, args.cluster_name, args.resource_pool, args.power_on,
                args.datastorecluster_name)
            if args.opaque_network_name:
                vm = pchelper.get_obj(content, [vim.VirtualMachine], args.vm_name)
                add_nic(si, vm, args.opaque_network_name)
        else:
            print("template not found")
"""


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