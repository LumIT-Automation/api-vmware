from pyVim.connect import SmartConnect, Disconnect
import ssl
import atexit
import random

from vmware.helpers.Singleton import Singleton

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException


class VmwareSupplicant(metaclass=Singleton):

    def __init__(self, dataConnection, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in [ "address", "port", "username", "password" ]:
            if key not in dataConnection:
                raise ValueError('Missing key in dataConnection dictionary.')

        self.ipAddr = dataConnection["address"]
        if dataConnection["port"]:
            self.port = dataConnection["port"]
        else:
            self.port = 443
        self.username = dataConnection["username"]
        self.password = dataConnection["password"]

        self.connection = None
        self.content = None
        self.silent = silent
        self.ran = random.random()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getContent(self) -> None:
        try:
            Log.actionLog("Get vmware contemt.")
            Log.log(self.ran, 'GGGGGGGGGGGEEEEEEEEEECCCCCCOOOOOOOOOONNNNNNNNNNNNNNNNNNNNNN')
            if not self.connection:
                self.__connect()

            self.content = self.connection.RetrieveContent()

        except Exception as e:
            raise e



    # Get all objects of type vimType.
    # vimTypes: vim.VirtualMachine, vim.Folder, vim.Datacenter, vim.VirtualApp, vim.ComputeResource, vim.Network, vim.Datastore.
    def getAllObjs(self, vimType: list = None) -> object:
        obj = {}
        vimType = [] if vimType is None else vimType

        Log.actionLog("Get all vmware objects.")
        Log.log(self.ran, 'GGGGGGGGGGGGGGGEEEEEEEEEEEEEE')

        if self.content:
            try:
                container = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimType, True)
                for managedObject_ref in container.view:
                    obj.update({managedObject_ref: managedObject_ref.name})

            except Exception as e:
                raise e

        return obj



    def disconnect(self) -> None:
        Log.log(self.ran, 'DDDDDDDDDDDDDDDDDDDIIIIIIIIIIIIIISSSSSSSSSSSSCCCCCCCCCCCC')
        try:
            Disconnect(self.content)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private  methods
    ####################################################################################################################

    def __connect(self) -> None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        Log.actionLog("Try vmware python connection to " + str(self.ipAddr))
        Log.log(self.ran, 'CCCCCCOOOOOOOOOONNNNNNNNNNNNNEEEEEEEEEEEEECCCCCCCCCCCCTTTTT')

        try:
            self.connection = SmartConnect(host=self.ipAddr, user=self.username, pwd=self.password, port=self.port, connectionPoolTimeout=60, sslContext=context)
            atexit.register(Disconnect, self.connection)

        except Exception as e:
            raise e
