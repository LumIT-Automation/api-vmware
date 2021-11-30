from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class Datacenter:
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The moId is the VMware Managed Object Id. Can be obtained from the "_moId" property of a managed object.
        self.assetId = int(assetId)
        self.moId = moId



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter folders list using pvmomi (a rest api call can be used alse for this onw).
    def list(assetId, silent: bool = None) -> dict:
        datacenters = list()
        vClient = None

        try:
            vmware = Asset(assetId)
            vmwareInfo = vmware.info()
            dataConnection = vmwareInfo["dataConnection"]

            vClient = VmwareSupplicant(dataConnection, silent)
            vClient.getContent()

            rootFolder = vClient.content.rootFolder
            datacenters = Datacenter.folderDatacenterList(rootFolder, datacenters)

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e


    @staticmethod
    # Plain vCenter folders list using pvmomi (a rest api call can be used alse for this onw).
    def objectlist(assetId, silent: bool = None) -> dict:
        pass



    @staticmethod
    def folderDatacenterList(folder: vim.Folder, dcList: []) -> list:
        try:
            children = folder.childEntity
            for c in children:
                if isinstance(c, vim.Datacenter):
                    dcList.append({
                        "moId": c._moId,
                        "name": c.name
                    })
                elif isinstance(c, vim.Folder):
                    Datacenter.folderDatacenterList(c, dcList)

            return dcList

        except Exception as e:
            raise e
