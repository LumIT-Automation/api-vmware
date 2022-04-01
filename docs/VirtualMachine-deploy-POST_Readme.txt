Virtual machine deploy POST:
    clone a template to a new virtual machine

    
    
#########
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
}
    
    "existent" dict key:
        - If the key missing, the disks of the templates are cloned as is.
        - If the key is present but the list is empty ( "existent": [], ), the disks of the template are not       copied in the new virtual machine (the vm can be diskless or have "new" disks only).
        - If the label of the disk doesn't match any label in the template, the deploy fail with 404 error.
        - If the size of the disk is greater than the size in the templare, the disk has grown. If it's smaller 
        the deploy will fail on vmware (http code 202 ACCEPT, the error is reported by celery in the stage2 db).
        - If the deviceType of the disk is different from the one in the template the disk is converted (if the storage support the format).
