from vmware.models.Permission.repository.Authorization import Authorization as Repository


class Authorization:

    # A permission "view".

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groups: list) -> dict:
        try:
            return Repository.list(groups)
        except Exception as e:
            raise e
