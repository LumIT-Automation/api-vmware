import ssl
import atexit
import random

from pyVim.connect import SmartConnect, Disconnect

from vmware.helpers.Log import Log


class VmwareSupplicant:
    def __init__(self, connectionData, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.ipAddr = connectionData["address"]
            self.port = connectionData["port"] \
                if connectionData["port"] else 443

            self.username = connectionData["username"]
            self.password = connectionData["password"]

            self.connection = None
            self.ran = random.random()
        except Exception:
            raise ValueError('Missing key in connection data.')



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
                raise e

        return self.connection



    def disconnect(self) -> None:
        try:
            Disconnect(self.connection)
        except Exception as e:
            raise e
