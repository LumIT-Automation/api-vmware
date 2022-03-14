
from vmware.models.Stage2.SshCommand import SshCommand
from vmware.helpers.Log import Log


class SshAddMountPoint(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        """ 
        Vars expected from the http PUT:
        "shellVars" = {
            "mountFolder": "/folder_where_mount",
            "vgNmae": "vg0",
            "lvName": "lv_name",
            "lvSize": 10,
            "filesystem": "ext4"
        }
        """

        # Variables passed to the shell script via shellVars.
        self.shellVars = """
            vg={vgName}
            lv={lvName}
            size={lvSize}
            folder={mountFolder}
            fs={filesystem}
        """

        self.command = """
            echo "lvcreate -n $lv -L ${size}G $vg"
            lvcreate -n $lv -L ${size}G $vg
            echo "mkfs.${fs} /dev/${vg}/${lv}"
            mkfs.${fs} /dev/${vg}/${lv}
            mkdir -p $folder

            if ! grep -q "/dev/${vg}/${lv}" /etc/fstab; then       
                echo -e "/dev/${vg}/${lv}\t${folder}\t$fs\tdefaults\t0\t2" >> /etc/fstab
            fi
            
            mount -a
        """
