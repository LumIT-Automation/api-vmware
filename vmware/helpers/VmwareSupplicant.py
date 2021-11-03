
from pyVim.connect import SmartConnect, Disconnect
import ssl
import atexit
from pyVmomi import vim, vmodl

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException


class VmwareSupplicant:

    def __init__(self, dataConnection: dict, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in [ "ip", "port", "username", "password" ]:
            if key not in dataConnection:
                raise ValueError('Missing key in dataConnection dictionary.')

        self.ipAddr = dataConnection["ip"]
        if dataConnection["port"]:
            self.port = dataConnection["port"]
        else:
            self.port = 443
        self.username = dataConnection["username"]
        self.password = dataConnection["password"]

        self.silent = silent



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getContent(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE

        try:
            Log.actionLog("Try vmware python connection to " + str(self.ipAddr))
            connection = SmartConnect(host=self.ipAddr, user=self.username, pwd=self.password, port=self.port, sslContext=context)
            atexit.register(Disconnect, connection)
            content = connection.RetrieveContent()

        except Exception as e:
            raise e

        return content
