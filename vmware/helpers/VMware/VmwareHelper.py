class VmwareHelper:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def getInfo(vmwareObj) -> dict:
        try:
            return dict({
                "moId": vmwareObj._GetMoId(),
                "name": vmwareObj.name
            })
        except Exception as e:
            raise e



    @staticmethod
    def getMoId(vmwareObj) -> str:
        try:
            return vmwareObj._GetMoId()
        except Exception as e:
            raise e



    @staticmethod
    def getType(moId: str) -> str:
        objectType = ""

        try:
            moIdPrefix = moId.split('-')[0]
            if moIdPrefix == "group":
                objectType = "folder"
            elif moIdPrefix == "domain":
                objectType = "cluster"
            elif moIdPrefix == "host":
                objectType = "host"
            elif moIdPrefix == "datacenter":
                objectType = "datacenter"
            elif moIdPrefix == "datastore":
                objectType = "datastore"
            elif moIdPrefix == "vm":
                objectType = "virtualmachine"
            elif moIdPrefix == "network" or moIdPrefix == "dvportgroup":
                objectType = "network"
        except Exception:
            pass

        return objectType
