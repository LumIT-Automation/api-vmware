
from vmware.commands.Stage2.SshCommand import SshCommand


class ResizeLastPartition(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)


        """ 
        Vars expected from the http PUT:
        "shellVars" = {
            "diskDevice": "sda",
        }
        """

        # Variables passed to the shell script via shellVars.
        self.shellVars = """
            # Given Disk name.
            dev={diskDevice}
        """

        self.command = """
            # Get the number of the last partition and if it's an LVM physical volume resize it.
            pN=0
            pNums=$(grep " ${dev}[0-9]" /proc/partitions | awk '{print $4}' | sed "s/${dev}//g")
            for n in $pNums; do
                if [ $n -gt $pN ]; then 
                    pN=$n
                fi
            done
            echo "Last partition: /dev/${dev}${pN}"
            
            # Resize the last partition if it's a pv, otherwise skip.
            if pvs /dev/${dev}${pN} > /dev/null 2>&1; then
                printf "d\n${pN}\nn\np\n${pN}\n\n\nt\n${pN}\n8e\nw\n" | fdisk /dev/${dev} || true
                sleep 0.5
                partprobe /dev/${dev}
                sleep 1
                pvresize /dev/${dev}${pN}
            else
                echo "Partition /dev/${dev}${pN} is not a physical volume. Skip it." 
            fi
        """
