
from vmware.models.Stage2.SshCommand import SshCommand


class SshRenameVg(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        getDefaultVg = 'defaultVg=$(vgs -o vg_name | tr -d " " | tail -n +2);'
        getVg = 'vgName="vg_`hostname -s`";'
        getSwapDevs = 'swapDevs=$(grep " swap " /etc/fstab | cut -d" " -f1);'
        swapOff = 'for dev in $swapDevs; do swapoff $dev; done;'
        vgRename = 'if ! vgrename $defaultVg $vgName; then exit 13; fi;'
        vgChange = 'vgchange -ay || exit 15;'
        updateFstab = 'sed -i -e "s#/${defaultVg}#/${vgName}#g" /etc/fstab;'
        getLvs = 'lVs=$(lvs -o lv_name | tr -d " " | tail -n +2);'
        refreshLvs = 'for lv in $lVs; do if ! lvchange /dev/${vgName}/$lv --refresh; then exit 17; fi; done;'

        debUpdateGrubCfg = '[ -w /boot/grub/grub.cfg ] && sed -i -e "s#/${defaultVg}#/${vgName}#" /boot/grub/grub.cfg;'
        debUpdateInitrdCfg = '[ -w /etc/initramfs-tools/conf.d/resume ] && sed -i -e "s#/${defaultVg}#/${vgName}#" /etc/initramfs-tools/conf.d/resume;'
        debUpdateInitrd = '[ -x /sbin/update-initramfs ] && if ! update-initramfs -u; then exit 19; fi;'

        rhGetRootDefaultLv = 'defaultRoot=$(grep " / " /etc/fstab | cut -f1 -d" ");' # Full path lv for root mount point (/dev/mapper/...-root
        rhGetRootLv = 'lvRoot=$(for lv in $A;do if grep " / " /etc/fstab | grep -q $lv;then echo $lv;fi;done);' # lv name for root mount point
        rhUpdateGrubCfg = '[ -w /boot/grub2/grub.cfg ] && sed -i -e "s#=${defaultVg}/#=${vgName}/#g" -e "s#${defaultRoot}#/dev/${vgName}/${lvRoot}g" /boot/grub2/grub.cfg;'
        rhUpdateGrubDefault = '[ -w /etc/default/grub ] && sed -i -e "s#=${defaultVg}/#=${vgName}/#g" /etc/default/grub;'
        rhUpdateGrubEnv = '[ -w /boot/grub2/grubenv ] && sed -i -e "s#=${defaultVg}/#=${vgName}/#g" -e "s#${defaultRoot}#/dev/${vgName}/${lvRoot}g /boot/grub2/grubenv;'

        reboot = 'reboot'

        self.command = getDefaultVg + getVg + getSwapDevs + swapOff + vgRename + vgChange + updateFstab #+ getLvs + \
        #    refreshLvs + debUpdateGrubCfg + rhGetRootDefaultLv + rhGetRootLv + rhUpdateGrubCfg + rhUpdateGrubEnv + \
        #    rhUpdateGrubDefault + debUpdateInitrdCfg + debUpdateInitrd + reboot

