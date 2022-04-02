Virtual machine deploy POST:
clone a template to a new virtual machine

BODY FIELDS:

"vmName": str, <- The name of the new virtual machine, mandatory.
"datacenterMoId": str <- The moId of the datacenter where to put the new virtual machine.
"clusterMoId": str <- The moId of the cluster where to put the new virtual machine.
"hostMoId": str <- The moId of the host where to put the new virtual machine. Alternative to "clusterMoId" OR preferred host in the cluster.
"vmFolderMoId": str <- The moId of the virtual machine folder where to put the new virtual machine.
"mainDatastoreMoId"::str <- The moId of the datastore where to put the new virtual machine. Must be connected to the host where the virtual machine is deployed.
"powerOn": bool <- Whether power on the VM after the deploy or not (default false).
"notes": str, <- An optional comment for the VM.
"guestSpce" str, <- The customization specification for the OS in the VM, to set hostname, ip address, etc.

##################### VM HARDWARE
"numCpu": int,
"numCoresPerSocket": int,
"memoryMB": int,


If a field is missing, the device/attribute is cloned as is.

    
############## DISK DEVICES
diskDevices": {
    "existent": [                   <-- disks present in the template, can be modified or deleted
        {
            "label": "Hard disk 1",
            "datastoreMoId": "datastore-2341",
            "sizeMB": 786,
            "deviceType": "thin"
        }
    
    ],
    
    "new": [
        {
            "label": "Hard disk 2",
            "datastoreMoId": "datastore-1366",
            "sizeMB": 2048,
            "deviceType": "thin"
        }    
    ]                       <-- new disks to be added to the new virtual machine
},

"existent" dict key:
    - If the key is missing, the disks of the templates are cloned as is.
    - If the key is present but the list is empty ( "existent": [], ) the disks of the template are not
        copied in the new virtual machine (the vm can be diskless or have "new" disks only).
    - If the label of a disk doesn't match any label in the template, the deploy fail with a 400 error.
    - If the size of the disk is greater than the size of the disk in the template with the same label, the disk has grown. If it's smaller
        the deploy will fail on vmware (http code 202 ACCEPT, the error is reported by celery in the stage2 db).
    - If the deviceType of a disk is different from the one in the template with the same label the disk is converted (if the storage support the format).
    - If the datastoreMoId is not valid (there is not a datastore with that moId or the datastore is not connected with that host/cluster)
        the deploy fail with a 400 error.

"new" dict key:
    - If the key missing, no new disk are added.
    - If the key is present but the list is empty ( "new": [], ) no new disks are added.
    - The "label" field for "new" devices can be present but it's ignored (vmware choose the label).
    - If the datastoreMoId is not valid (there is not a datastore with that moId or the datastore is not connected with that host/cluster)
        the deploy fail with a 400 error.


############## NETWORK DEVICES
"networkDevices": {
    "existent": [
        {
            "networkMoId": "network-1213",
            "label": "Network adapter 1",
            "deviceType": "vmxnet3"
        }
    ],
    "new": [
        {
            "networkMoId": "network-1213",
            "label": "Network adapter 2",
            "deviceType": "vmxnet2"
        }

    ]
},

"existent" dict key:
    - If the key is missing, the nics of the templates are cloned as is.
    - If the key is present but the list is empty ( "existent": [], ), the nics of the template are not
        copied in the new virtual machine (the vm can be without network cards or have "new" nics only).
    - If the label of a nic doesn't match any label in the template, the deploy fail with a 400 error.
    - If the deviceType of a nic is different from the one in the template with the same label the deviceType of the nic is changed.
    - If the networkMoId is not valid (there is not a network with that moId) the deploy fail with a 400 error.

"new" dict key:
    - If the key missing, no new nics are added.
    - If the key is present but the list is empty ( "new": [], ) no new nics are added.
    - The "label" field for "new" devices can be present but it's ignored (vmware choose the label).
    - If the networkMoId is not valid (there is not a network with that moId) the deploy fail with a 400 error.