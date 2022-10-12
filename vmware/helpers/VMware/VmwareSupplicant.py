import ssl
import atexit
import random

from pyVim.connect import SmartConnect, Disconnect

from vmware.models.VMware.Asset import Asset
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VmwareSupplicant:
    def __init__(self, asset: Asset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.ipAddr = asset.address
            self.port = asset.port if asset.port else 443
            self.username = asset.username
            self.password = asset.password

            self.connection = None # this is a vim.ServiceInstance object.
            self.ran = random.random()
        except Exception:
            raise ValueError('Error in connection data.')



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def connect(self):
        if not self.connection:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE

            try:
                Log.actionLog("["+str(self.ran)+"] Connecting to VMware server: "+str(self.ipAddr))

                self.connection = SmartConnect(
                    host=self.ipAddr,
                    user=self.username,
                    pwd=self.password,
                    port=self.port,
                    connectionPoolTimeout=60,
                    sslContext=context
                )
                atexit.register(Disconnect, self.connection)
            except Exception as e:
                raise Exception("vmware supplicant", e.args)

        return self.connection



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def disconnect(connection: object) -> None:
        try:
            Disconnect(connection)
        except Exception as e:
            raise e
