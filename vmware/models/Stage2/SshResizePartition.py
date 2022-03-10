
from vmware.models.Stage2.SshCommand import SshCommand


class SshResizePartition(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        getDiskdevs = 'diskDev=$(lsblk -i | grep disk | cut -f1 -d" ");'
        getPartNumbers = "pNum=$(grep ' sda[0-9]' /proc/partitions | awk '{print $4}' |sed 's/sda//g');"
        getLastPartNumber = 'N=0; for n in $pNum; do if [ $n -gt $N ]; then N=$n;fi;done;'
        echoLastPart = 'echo "partition: /dev/${diskDev}${N}";'
        checkPartIsPv = 'if ! pvs /dev/${diskDev}${N} > /dev/null 2>&1; then exit 5; fi;'
        lastPartResize = 'if ! printf "d\n${N}\nn\np\n${N}\n\n\nt\n${N}\n8e\nw\n" | fdisk /dev/${diskDev}; then exit 7; fi;'
        partProbe = 'partprobe; sleep 1;'
        pvResize = 'if ! pvresize /dev/${diskDev}${N}; then exit 9; fi;'

        self.command = getDiskdevs + getPartNumbers + getLastPartNumber + echoLastPart + checkPartIsPv + lastPartResize + partProbe + pvResize

