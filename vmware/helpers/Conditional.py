from typing import Union

import hashlib
import json


class Conditional:
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def responseEtagFreshnessAgainstRequest(self, result: Union[dict, str]) -> dict:
        # Compares the resource's hash against the passed If-None-Match HTTP header
        # in order to state if the resource corresponding to the header is fresh or not.
        ifNoneMatchRequest = ""

        # Get the If-None-Match request header.
        if "If-None-Match" in self.request.headers:
            ifNoneMatchRequest = self.request.headers['If-None-Match'].strip()

        # Calculate the ETag value for the response.
        eTag = hashlib.sha256(json.dumps(result).encode('utf-8')).hexdigest().strip()

        if ifNoneMatchRequest != eTag:
            state = "stale"
        else:
            state = "fresh"

        return {
            "state": state,
            "responseEtag": eTag
        }
