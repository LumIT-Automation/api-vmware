from vmware.repository.Permission.Authorization import Authorization as Repository


class Authorization:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groups: list) -> dict:
        try:
            return Repository.list(groups)
        except Exception as e:
            raise e
