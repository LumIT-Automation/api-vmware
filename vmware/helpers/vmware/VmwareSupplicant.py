import ssl
import atexit
import random

from pyVim.connect import SmartConnect, Disconnect

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class VmwareSupplicant(metaclass=Singleton):
    def __init__(self, connectionData, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.ipAddr = connectionData["address"]
            self.port = connectionData["port"] \
                if connectionData["port"] else 443

            self.username = connectionData["username"]
            self.password = connectionData["password"]

            self.connection = None
            self.content = None

            self.ran = random.random()
        except Exception:
            raise ValueError('Missing key in connection data.')



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def fetchContent(self) -> None:
        try:
            if not self.connection:
                self.__connect()

            self.content = self.connection.RetrieveContent()
        except Exception as e:
            raise e



    # Get objects of type vimType.
    # vimTypes: vim.VirtualMachine, vim.Folder, vim.Datacenter, vim.VirtualApp, vim.ComputeResource, vim.Network, vim.Datastore.
    def getObjects(self, vimType: list = None) -> dict:
        obj = {}
        vimType = [] if vimType is None else vimType

        try:
            if not self.content:
                Log.actionLog("["+str(self.ran)+"] Get VMware "+str(vimType)+" objects.")
                self.fetchContent()

            if self.content:
                c = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimType, True)
                for managedObject_ref in c.view:
                    obj[managedObject_ref] = managedObject_ref.name
            else:
                raise CustomException(status=400, payload={"VMware": "cannot fetch VMware objects."})
        except Exception as e:
            raise e

        return obj



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __connect(self) -> None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE

        try:
            Log.actionLog("Connecting to VMware server: "+str(self.ipAddr))

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



    def __disconnect(self) -> None:
        try:
            Disconnect(self.content)
        except Exception as e:
            raise e
