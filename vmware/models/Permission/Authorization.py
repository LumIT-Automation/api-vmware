from vmware.models.Permission.IdentityGroup import IdentityGroup



class Authorization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groups: list) -> dict:
        permissions = list()
        combinedPermissions = dict()

        o = IdentityGroup.list(True)

        # Collect every permission related to the group in groups.
        for identityGroup in groups:
            for el in o["items"]:
                if "identity_group_identifier" in el:
                    if el["identity_group_identifier"].lower() == identityGroup.lower():
                        permissions.append(el["privileges_vmFolder"])

        #[
        #    {
        #        "assets_get": [
        #            {
        #                "assetId": "1",
        #                "vmFolder": "any"
        #            }
        #        ],
        #        ...
        #    },
        #    {
        #        "assets_get": [
        #            {
        #                "assetId": "1",
        #                "vmFolder": "Common"
        #            }
        #        ],
        #        ...
        #    }
        #]

        # Clean up structure.
        for el in permissions:
            for k, v in el.items():

                # Initialize list if not already done.
                if not str(k) in combinedPermissions:
                    combinedPermissions[k] = list()

                for innerEl in v:
                    if innerEl not in combinedPermissions[k]:
                        combinedPermissions[k].append(innerEl)

        #{
        #    ...
        #    "assets_get": [
        #        {
        #            "assetId": "1",
        #            "vmFolder": "any"
        #        },
        #        {
        #            "assetId": "1",
        #            "vmFolder": "Common"
        #        },
        #        {
        #            "assetId": "2",
        #            "vmFolder": "Common"
        #        }
        #    ],
        #    ...
        #}

        # Clean up structure.
        for k, v in combinedPermissions.items():
            asset = 0
            for el in v:
                if el["vmFolder"] == "any":
                    asset = el["assetId"] # assetId for vmFolder "any".

            if asset:
                for j in range(len(v)):
                    try:
                        if v[j]["assetId"] == asset and v[j]["vmFolder"] != "any":
                            del v[j]
                    except Exception:
                        pass

        #{
        #    ...
        #    "assets_get": [
        #        {
        #            "assetId": "1",
        #            "vmFolder": "any"
        #        },
        #        {
        #            "assetId": "2",
        #            "vmFolder": "Common"
        #        }
        #    ],
        #    ...
        #}

        return dict({
            "items": combinedPermissions
        })
