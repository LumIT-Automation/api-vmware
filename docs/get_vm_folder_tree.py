#!/usr/bin/python

from pyVim.connect import SmartConnect, Disconnect
import ssl
import atexit
from pyVmomi import vim, vmodl

def connect(hostname, username, password):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE

    si = SmartConnect(host=hostname, user=username,
                      pwd=password, port=443, sslContext=context)
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    return content

hostname = ''
username = ''
password = ''

content = connect(hostname, username, password)

#all_vms = get_all_objs(content, [vim.vmFolder])
#all_vms = get_all_objs(content, [vim.VirtualMachine])
#for item in list(all_vms.keys()):
#    print(get_folder_path(item))

dcs = content.rootFolder.childEntity
#for dc in dcs:
#    children = dc.vmFolder.childEntity
#    for child in children:
#        if isinstance(child, vim.Folder):
#            print(child, child.name, child.parent)

def folderTree(folder, tree: {}):
    if isinstance(folder, vim.Folder):
        children = folder.childEntity
        for child in children:
            if isinstance(child, vim.Folder):
                subTree = { child: {
                    "name":  child.name,
                    "subFolders": {}
                    }
                }
                tree[folder]["subFolders"].update(subTree)
                folderTree(child, subTree)
    return tree


for dc in dcs:
    parentFolder = dc.vmFolder

    tree = { parentFolder: {
        "name": dc.name,
        "subFolders": {}
        }
    }

    print(folderTree(parentFolder, tree))

Disconnect(content)
