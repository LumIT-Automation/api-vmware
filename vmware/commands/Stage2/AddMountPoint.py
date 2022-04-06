
from vmware.commands.Stage2.SSHCommand import SSHCommand


class AddMountPoint(SSHCommand):
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
            # Use /proc to find all processes that have opened file descriptors in the given folder.
            folder_stop_all_processes() {
                if [ -z "$1" ]; then
                    echo "Usage: $0 <folder>"
                    exit 0
                fi
                folder="$1"
                                
                echo "$0: stop all"
                # Try to stop the processes with a SIGTERM first.
                cd /proc
                for PID in `ls -d [0-9]*`; do 
                    if ls -l ${PID}/fd 2>/dev/null | grep -q "$folder"; then
                        if ! ps -up $PID | grep -Eq "sshd|bash|sudo"; then 
                            kill $PID
                        fi 
                    fi
                done
                
                sleep 1
                
                # If SIGTERM is not enough, seng SIGKILL.
                echo "$0: kill all"
                cd /proc
                for PID in `ls -d [0-9]*`; do 
                    if ls -l ${PID}/fd 2>/dev/null | grep -q "$folder"; then
                        if ! ps -up $PID | grep -Eq "sshd|bash|sudo"; then 
                            kill -9 $PID
                        fi 
                    fi
                done
            }
            
            clone_folder() {
                if [ -z "$1" ] || [ -z "$2" ]; then
                    echo "Usage: $0 <folder>"
                    exit 0
                fi
                folder="$1"
                dstFolder="$2"
                
                cd $folder || exit 111
                echo "$0: tar --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar --xattrs --acls xpf -)"
                tar --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar xpf -)
            }

            tmpMount="" # Global variable to get the value from tmp_mount() function.
            tmp_mount() {
                if [ -z "$1" ]; then
                    echo "Usage: $0 <mount_device>"
                    exit 0
                fi
                mountDev="$1"
                mountDir=`mktemp -d`
                echo "mount $mountDev $mountDir"
                mount $mountDev $mountDir || exit 121
                tmpMount=$mountDir
            }
            if ! vgs -o vg_name | grep -q " ${vg}"; then
                echo "Volume group not found."
                exit 11
            fi
            if lvs -o lv_name | grep -q " $lv "; then
                echo "lv $lv already existent"
            else
                echo "lvcreate -n $lv -L ${size}G $vg"
                if ! lvcreate -n $lv -L ${size}G $vg; then
                    echo "can't create lv $lv"
                    exit 13
                fi
            fi
            
            if lsblk -n -o FSTYPE /dev/${vg}/${lv} | grep -Eq 'ext[2-4]|xfs|btrfs'; then
                echo "lv $lv already formatted"
            else
                echo "mkfs.${fs} /dev/${vg}/${lv}"
                if ! mkfs.${fs} /dev/${vg}/${lv}; then
                    echo "can't format /dev/${vg}/${lv}"
                    exit 15
                fi
            fi
            
            if mount  | grep "$folder" | grep -E `lvs --noheadings -o lv_dm_path,lv_path /dev/${vg}/${lv} | sed -r -e 's/^ +//g' | tr ' ' '|'`; then
                echo "lv $lv already mounted on $folder"
                # TODO: check lv size here.
            else
                # The folder is already present (but not mounted on $lv), stop processes on it amd move the data.
                if [ -d "$folder" ]; then
                    folder_stop_all_processes $folder
                    tmp_mount "/dev/${vg}/${lv}"
                    clone_folder $folder $tmpMount
                    cd $folder && rm -fr * # cleanup the data in the old place.
                    cd
                    echo "umount -l "/dev/${vg}/${lv}" && rm -fr $tmpMount"
                    umount -l "/dev/${vg}/${lv}" && rm -fr $tmpMount
                else
                    mkdir -p $folder || exit 17
                fi
                mount /dev/${vg}/${lv} $folder
            fi
                      
            if ! grep -q "/dev/${vg}/${lv}" /etc/fstab; then
                echo "echo -e \"/dev/${vg}/${lv}\t${folder}\t$fs\tdefaults\t0\t2\" >> /etc/fstab"    
                echo -e "/dev/${vg}/${lv}\t${folder}\t$fs\tdefaults\t0\t2" >> /etc/fstab
            fi
            
        """
