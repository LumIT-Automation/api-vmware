
from vmware.commands.Stage2.SshCommand import SshCommand


class RenameVg(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        self.command = """
            # Get default vg name.
            defVg=$(vgs --noheadings -o vg_name | tr -d " ")
            echo "defVg: $defVg"
            # Wanted vg name.
            vg="vg_`hostname -s`"
            echo "vg: $vg"
            # Get all lv names.
            lVs=$(lvs --noheadings -o lv_name | tr -d " ")
            # Get default lv mapper path of the root lv.
            defRootLvPath=$(grep " / " /etc/fstab | cut -f1 -d" ")
            echo "defRootLvPath: $defRootLvPath"
            # Pick the lv name of the root lv.
            lvRoot=$(for lv in $lVs;do 
                if grep " / " /etc/fstab | grep -q $lv; then 
                    echo $lv
                fi
            done)
            
            # Swap devices in fstab. Hash: lv[lvname] = /dev/mapper/...
            declare -A swapDevs
            defSwapLvsPath=$(grep " swap " /etc/fstab | cut -d" " -f1)
            # Map lv path to lv names.
            for lv in $lVs;do
                lvPath=$(grep " swap " /etc/fstab | grep "\-${lv}" | cut -f1 -d " ")
                if [ -n "$lvPath" ]; then
                    swapDevs[${lv}]=$lvPath
                fi
            done
            # Stop swaps.
            for dev in $defSwapLvsPath; do 
                swapoff $dev
            done
            
            # Other devices in fstab. Hash: lv[lvname] = /dev/mapper/...
            declare -A otherDevs
            defOtherLvsPath=$(grep -v ' / | swap' /etc/fstab | grep -E 'ext4|ext3|xfs|brtfs' | grep -E "/dev/mapper|/dev/${defVg}" | cut -d" " -f1)
            # Map lv path to lv names, exclude root and swaps.         
            for lv in $lVs;do
                lvPath=$(grep -Ev ' / | swap' /etc/fstab | grep -E 'ext4|ext3|xfs|brtfs' | grep "\-${lv}" | cut -f1 -d " ")
                if [ -n "$lvPath" ]; then
                    otherDevs[${lv}]=$lvPath
                fi
            done
                     
            # Rename volume group
            if ! vgrename $defVg $vg; then 
                exit 13
            fi
            # Reactivate vg and lvs.
            vgchange -ay || exit 15
            for lv in $lVs; do 
                if ! lvchange /dev/${vg}/$lv --refresh; then 
                    exit 17
                fi
            done
            
            # Vg renamed: can get the new lv mapper path of the root lv.
            rootMap=$(lvs --noheadings -o lv_path -S lv_name=$lvRoot | tr -d " ")
            echo "rootMap: $rootMap"

            # Adjust fstab.
            sed -i -e "s#${defRootLvPath}#${rootMap}#g" /etc/fstab # If mapper path was used.
            if [ -n $swapDevs ]; then
                for lv in "${!swapDevs[@]}"; do
                    sed -i -e "s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g" /etc/fstab
                done
            fi
            if [ -n $otherDevs ]; then
                for lv in "${!otherDevs[@]}"; do
                    sed -i -e "s#${otherDevs[$lv]}#/dev/${vg}/${lv}#g" /etc/fstab
                done
            fi
            sed -i -e "s#/${defVg}#/${vg}#g" /etc/fstab # If /dev/vgname/lvname was used.
            
            # Adjust grub.cfg, grubenv, default-grub. 
            for grubFile in /boot/grub/grub.cfg /boot/grub2/grub.cfg /boot/grub/grubenv /boot/grub2/grubenv /etc/default/grub /etc/sysconfig/grub; do 
                if [ -w $grubFile ]; then
                    sed -i -e "s#${defRootLvPath}#${rootMap}#g" $grubFile
                    sed -i -e "s#/${defVg}#/${vg}#g" -e "s#${defVg}/#${vg}/#g" $grubFile
                fi
            done
                
            # initramfs (adjust swap).
            if [ -w /etc/initramfs-tools/conf.d/resume ]; then
                for lv in "${!swapDevs[@]}"; do
                    sed -i -e "s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g" /etc/initramfs-tools/conf.d/resume
                done
                sed -i -e "s#/${defVg}#/${vg}#" /etc/initramfs-tools/conf.d/resume
            fi
            if [ -x /sbin/update-initramfs ]; then
                if ! update-initramfs -u; then 
                    exit 19
                fi
            fi
            if [ -x /sbin/dracut ]; then
                dracut --force
            fi
            
        """

