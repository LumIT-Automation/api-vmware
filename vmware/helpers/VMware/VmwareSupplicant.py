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

            self.vmwareServiceInstance = None # vim.ServiceInstance object, root of the vSphere inventory.
            self.ran = random.random()
        except Exception:
            raise ValueError('Error in connection data.')



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def connect(self):
        if not self.vmwareServiceInstance:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE

            try:
                Log.actionLog("["+str(self.ran)+"] Connecting to VMware server: "+str(self.ipAddr))

                self.vmwareServiceInstance = SmartConnect(
                    host=self.ipAddr,
                    user=self.username,
                    pwd=self.password,
                    port=self.port,
                    connectionPoolTimeout=60,
                    sslContext=context
                )
                atexit.register(Disconnect, self.vmwareServiceInstance)
            except Exception as e:
                raise Exception("vmware supplicant", e.args)

        return self.vmwareServiceInstance



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def disconnect(vmwareServiceInstance: object) -> None:
        try:
            Disconnect(vmwareServiceInstance)
        except Exception as e:
            raise e
