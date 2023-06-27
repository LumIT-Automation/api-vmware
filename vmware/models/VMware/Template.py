from typing import List

from vmware.models.VMware.backend.VirtualMachine import VirtualMachine as Backend
from vmware.models.VMware.VirtualMachine import VirtualMachine

from vmware.helpers.VMware.VmwareHelper import VmwareHelper
from vmware.helpers.Exception import CustomException


class VirtualMachineTemplate(VirtualMachine):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, related: bool = True) -> dict:
        if not self.__isVmTemplate():
            raise CustomException(status=400, payload={"VMware": "This object is not a virtual machine template."})

        info = super().info()
        return info



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        virtualmachines = list()

        try:
            for o in Backend.oVirtualMachines(assetId):
                if o.config.template:
                    virtualmachine = VirtualMachine(assetId, VmwareHelper.getInfo(o)["moId"])
                    virtualmachines.append(
                        VirtualMachine._cleanup("list", virtualmachine.info(related))
                    )

            # Sort the list using "name" as sort key.
            def sortFunc(el: dict):
                return el["name"].lower()

            virtualmachines.sort(key=sortFunc)

            return virtualmachines
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        virtualmachines = list()

        try:
            for o in Backend.oVirtualMachines(assetId):
                if o.summary.config.template: # summary has a real value: it is not a lazy object as o.config.template.
                    virtualmachine = VmwareHelper.getInfo(o)
                    virtualmachine["assetId"] = assetId
                    virtualmachines.append(virtualmachine)

            # Sort the list using "name" as sort key.
            def sortFunc(el: dict):
                return el["name"].lower()

            virtualmachines.sort(key=sortFunc)

            return virtualmachines
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __isVmTemplate(self) -> bool:
        return bool(self.oVirtualMachine.config.template)
