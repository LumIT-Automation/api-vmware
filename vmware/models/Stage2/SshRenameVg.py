
from vmware.models.Stage2.SshCommand import SshCommand


class SshRenameVg(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        getDefaultVg = 'defaultVg=$(vgs -o vg_name | tr -d " " | tail +2);'
        getVg = 'vgName="vg_`hostname -s`";'
        getSwapDevs = 'swapDevs=$(grep " swap " /etc/fstab | cut -d" " -f1);'
        swapOff = 'for dev in $swapDevs; do if ! swapoff $dev; then exit 11; fi; done;'
        vgRename = 'if ! vgrename $defaultVg $vgName; then exit 13; fi;'
        vgChange = 'vgchange -ay || exit 15;'
        updateFstab = 'sed -i -e "s#/${defaultVg}#/${vgName}#g" /etc/fstab;'
        getLvs = 'lVs=$(lvs -o lv_name | tr -d " " | tail +2);'
        refreshLvs = 'for lv in $lVs; do if ! lvchange /dev/${vgName}/$lv --refresh; then exit 17; fi; done;'
        debUpdateInitrdCfg = '[ -w /etc/initramfs-tools/conf.d/resume ] && sed -i -e "s#/${defaultVg}#/${vgName}#" /etc/initramfs-tools/conf.d/resume;'
        debUpdateGrub = '[ -w /boot/grub/grub.cfg ] && sed -i -e "s#/${defaultVg}#/${vgName}#" /boot/grub/grub.cfg;'
        debUpdateInitrd = '[ -x /sbin/update-initramfs ] && if ! update-initramfs -u; then exit 19; fi;'
        reboot = 'reboot'

        self.command = getDefaultVg + getVg + getSwapDevs + swapOff + vgRename + vgChange + updateFstab + getLvs + \
            refreshLvs + debUpdateGrub + debUpdateInitrdCfg + debUpdateInitrd + reboot

