
from vmware.models.Stage2.SshCommand import SshCommand


class LvsGrow(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)


        """ 
        Vars expected from the http PUT:
        "shellVars" = {
            "vgNmae": "vg0",
            "lvName": "lv_name",
            "totSize": 10,
            "growSize": 2,
            "grow_100": False
        }
        """
        # Order of precedence:
        # 1) if grow_100 is true, use lvextend -l +100%FRE device
        # 2) if $totSize is given, use lvextend -L${totSize}G device
        # 3) if $growSize is given, use lvextend -L+${growSize}G device

        # Variables passed to the shell script via shellVars.
        self.shellVars = """
            vg={vgName}
            lv={lvName}
            totSize={totSize}
            growSize={growSize}
            grow_100={grow_100}
        """

        self.command = """
            # Check lv
            if [ ! -b /dev/${vg}/${lv} ]; then
                echo /dev/${vg}/${lv}
                exit 31    
            fi

            if [ "$grow_100" == "True" ]; then
                echo "lvextend -l +100%FREE /dev/${vg}/${lv}"   
                if ! lvextend -l +100%FREE /dev/${vg}/${lv}; then
                    echo "Error on executing lvextend" 
                fi
            elif [ $totSize -gt 0 ]; then
                echo "lvextend -L${totSize}G /dev/${vg}/${lv}"
                if ! lvextend -L${totSize}G /dev/${vg}/${lv}; then
                    echo "Error on executing lvextend"
                fi
            elif [ -n "$growSize" ]; then
                echo "lvextend -L+${growSize}G /dev/${vg}/${lv}"
                if ! lvextend -L+${growSize}G /dev/${vg}/${lv}; then
                    echo "Error on executing lvextend"
                fi
            fi
            
            if file -sL /dev/${vg}/${lv} | grep -Eq 'ext4|ext3|ext2'; then
                resize2fs /dev/${vg}/${lv}
            elif file -sL /dev/${vg}/${lv} | grep -iq 'xfs'; then
                xfs_growfs /dev/${vg}/${lv}
            elif file -sL /dev/${vg}/${lv} | grep -iq 'btrfs'; then
                # A mount point it's needed to grow a btrs.
                mPoint=`mount | grep /dev/${vg}/${lv} | cut -f3 -d " "`
                if [ -z "$mPoint" ]; then
                    dmPath=`lvs --noheadings -o lv_dmpath /dev/${vg}/${lv} | tr -d " "`
                    mPoint=`mount | grep "$dmPath" | cut -f3 -d " "`
                fi
                if [ -n "$mPoint" ]; then
                    echo "btrfs filesystem resize max $mPoint"
                    btrfs filesystem resize max $mPoint
                else
                    echo "Cannot find mount point for /dev/${vg}/${lv}"
                fi
            else
                echo "Can't identify the filesystem on the device /dev/${vg}/${lv}, do not grow the filesystem."
                exit 121
            fi
        """
