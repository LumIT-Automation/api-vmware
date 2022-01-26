class VmwareHelper:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def vmwareObjToDict(vmwareObj) -> dict:
        try:
            return dict({
                "moId": vmwareObj._GetMoId(),
                "name": vmwareObj.name
            })
        except Exception as e:
            raise e
