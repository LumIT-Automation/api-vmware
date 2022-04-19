-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Ago 02, 2021 alle 08:22
-- Versione del server: 10.3.27-MariaDB-0+deb10u1-log
-- Versione PHP: 7.3.27-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `stage2`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `target`
--

CREATE TABLE `target` (
  `id` int(11) NOT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `port` int(11) DEFAULT NULL,
  `api_type` varchar(64) NOT NULL DEFAULT '',
  `id_bootstrap_key` INT DEFAULT NULL,
  `username` varchar(64) NOT NULL DEFAULT '',
  `password` varchar(64) NOT NULL DEFAULT '',
  `id_asset` int(11) DEFAULT NULL,
  `task_moid` varchar(64) DEFAULT NULL,
  `task_state` varchar(64) NOT NULL DEFAULT 'undefined',
  `task_progress` int DEFAULT NULL,
  `task_startTime` varchar(64) NOT NULL DEFAULT '',
  `task_queueTime` varchar(64) NOT NULL DEFAULT '',
  `task_message` varchar(512) NOT NULL DEFAULT '',
  `second_stage` varchar(8192) NOT NULL DEFAULT '[]' CHECK (json_valid(`second_stage`)),
  `vm_name` varchar(128) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `bootstrap_key`
--

CREATE TABLE `bootstrap_key` (
  `id` int(11) NOT NULL,
  `priv_key` varchar(65536) NOT NULL DEFAULT '',
  `comment` varchar(1024) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `group_pubkey`
--

CREATE TABLE `final_pubkey` (
  `id` int(11) NOT NULL,
  `comment` varchar(1024) NOT NULL DEFAULT '',
  `pub_key` varchar(2048) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `command`
--

CREATE TABLE `command` (
  `uid` varchar(64) NOT NULL,
  `command` text NOT NULL,
  `template_args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`template_args`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `target_command`
--

CREATE TABLE `target_command` (
  `id_target` int(11) NOT NULL,
  `command` varchar(64) NOT NULL DEFAULT '',
  `user_args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`user_args`)),
  `sequence` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `command_exec_status`
--

CREATE TABLE `command_exec_status` (
  `id` int(11) NOT NULL,
  `id_command` varchar(64) NOT NULL,
  `exec_count` tinyint(4) NOT NULL,
  `exit_status` int(11) NOT NULL,
  `stdout` mediumtext NOT NULL DEFAULT '',
  `stderr` mediumtext NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `target`
--
ALTER TABLE `target`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ip` (`ip`),
  ADD UNIQUE KEY `taskId` (`id_asset`,`task_moid`);

--
-- Indici per le tabelle `bootstrap_key`
--
ALTER TABLE `bootstrap_key`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `group_pubkey`
--
ALTER TABLE `final_pubkey`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `command`
--
ALTER TABLE `command`
  ADD PRIMARY KEY (`uid`);
COMMIT;

--
-- Indici per le tabelle `command_exec_status`
--
ALTER TABLE `command_exec_status`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ces_command` (`id_command`);

--
-- Indici per le tabelle `target_command`
--
ALTER TABLE `target_command`
  ADD PRIMARY KEY (`id_target`,`command`),
  ADD KEY `tc_command` (`command`);


--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `target`
--
ALTER TABLE `target`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `bootstrap_key`
--
ALTER TABLE `bootstrap_key`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `final_pubkey`
--
ALTER TABLE `final_pubkey`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `command_exec_status`
--
ALTER TABLE `command_exec_status`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `target`
--
ALTER TABLE `target`
  ADD CONSTRAINT `bk_key` FOREIGN KEY (`id_bootstrap_key`) REFERENCES `bootstrap_key` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `target_command`
--
ALTER TABLE `target_command`
  ADD CONSTRAINT `tc_command` FOREIGN KEY (`command`) REFERENCES `command` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tc_target` FOREIGN KEY (`id_target`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

--
-- Limiti per la tabella `command_exec_status`
--
ALTER TABLE `command_exec_status`
  ADD CONSTRAINT `ces_command` FOREIGN KEY (`id_command`) REFERENCES `command` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;


-- --------------------------------------------------------

--
-- Dump dei dati per la tabella `command`
--

INSERT INTO `command` (`uid`, `command`, `template_args`) VALUES
('addPubKey', '#/bin/bash\n\nset -e\n\npubKey=${__pubKey}\n\nif ! grep -q \"${pubKey}\" /root/.ssh/authorized_keys; then echo \"${pubKey}\" >> /root/.ssh/authorized_keys; fi', '{}'),
('addMountPoint', '#/bin/bash\n\nset -e\n\nvg=${__vgName}\nlv=${__lvName}\nsize=${__lvSize}\nfolder=${__mountFolder}\nfs=${__filesystem}\n\n# Use /proc to find all processes that have opened file descriptors in the given folder.\nfolder_stop_all_processes() {\n    if [ -z \"$1\" ]; then\n        echo \"Usage: $0 <folder>\"\n        exit 0\n    fi\n    folder=\"$1\"\n                    \n    echo \"$0: stop all\"\n    # Try to stop the processes with a SIGTERM first.\n    cd /proc\n    for PID in `ls -d [0-9]*`; do \n        if ls -l ${PID}/fd 2>/dev/null | grep -q \"$folder\"; then\n            if ! ps -up $PID | grep -Eq \"sshd|bash|sudo\"; then \n                kill $PID\n            fi \n        fi\n    done\n    \n    sleep 1\n    \n    # If SIGTERM is not enough, seng SIGKILL.\n    echo \"$0: kill all\"\n    cd /proc\n    for PID in `ls -d [0-9]*`; do \n        if ls -l ${PID}/fd 2>/dev/null | grep -q \"$folder\"; then\n            if ! ps -up $PID | grep -Eq \"sshd|bash|sudo\"; then \n                kill -9 $PID\n            fi \n        fi\n    done\n}\n\nclone_folder() {\n    if [ -z \"$1\" ] || [ -z \"$2\" ]; then\n        echo \"Usage: $0 <folder>\"\n        exit 0\n    fi\n    folder=\"$1\"\n    dstFolder=\"$2\"\n    \n    cd $folder || exit 111\n    echo \"$0: tar --selinux --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar --selinux --xattrs --acls xpf -)\"\n    tar --selinux --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar --selinux --xattrs --acls --xattrs-include=* -x -p -f -)\n}\n\ntmpMount=\"\" # Global variable to get the value from tmp_mount() function.\ntmp_mount() {\n    if [ -z \"$1\" ]; then\n        echo \"Usage: $0 <mount_device>\"\n        exit 0\n    fi\n    mountDev=\"$1\"\n    mountDir=`mktemp -d`\n    echo \"mount $mountDev $mountDir\"\n    mount $mountDev $mountDir || exit 121\n    tmpMount=$mountDir\n}\nif ! vgs -o vg_name | grep -q \" ${vg}\"; then\n    echo \"Volume group not found.\"\n    exit 11\nfi\nif lvs -o lv_name | grep -q \" $lv \"; then\n    echo \"lv $lv already existent\"\nelse\n    echo \"lvcreate -n $lv -L ${size}G $vg\"\n    if ! lvcreate -n $lv -L ${size}G $vg; then\n        echo \"can\'t create lv $lv\"\n        exit 13\n    fi\nfi\n\nif lsblk -n -o FSTYPE /dev/${vg}/${lv} | grep -Eq \'ext[2-4]|xfs|btrfs\'; then\n    echo \"lv $lv already formatted\"\nelse\n    echo \"mkfs.${fs} /dev/${vg}/${lv}\"\n    if ! mkfs.${fs} /dev/${vg}/${lv}; then\n        echo \"can\'t format /dev/${vg}/${lv}\"\n        exit 15\n    fi\nfi\n\nif mount  | grep \"$folder\" | grep -E `lvs --noheadings -o lv_dm_path,lv_path /dev/${vg}/${lv} | sed -r -e \'s/^ +//g\' | tr \' \' \'|\'`; then\n    echo \"lv $lv already mounted on $folder\"\n    # TODO: check lv size here.\nelse\n    # The folder is already present (but not mounted on $lv), stop processes on it amd move the data.\n    if [ -d \"$folder\" ]; then\n        folder_stop_all_processes $folder\n        tmp_mount \"/dev/${vg}/${lv}\"\n        clone_folder $folder $tmpMount\n        cd $folder && rm -fr * || true # cleanup the data in the old place.\n        cd\n        echo \"umount -l \"/dev/${vg}/${lv}\" && rm -fr $tmpMount\"\n        umount -l \"/dev/${vg}/${lv}\" && rm -fr $tmpMount\n    else\n        mkdir -p $folder || exit 17\n    fi\n    mount /dev/${vg}/${lv} $folder\nfi\n          \nif ! grep -q \"/dev/${vg}/${lv}\" /etc/fstab; then\n    echo \"echo -e \\\"/dev/${vg}/${lv}\\t${folder}\\t$fs\\tdefaults\\t0\\t2\\\" >> /etc/fstab\"    \n    echo -e \"/dev/${vg}/${lv}\\t${folder}\\t$fs\\tdefaults\\t0\\t2\" >> /etc/fstab\nfi\n\nmount | grep "$folder"\n', '{\n\"__vgName\": \"str\",\n\"__lvName\": \"str\",\n\"__lvSize\": \"int\",\n\"__mountFolder\": \"str\",\n\"__filesystem\": \"str\"\n}'),
('echo', '#/bin/bash\n\nset -e\n\necho \"${__echo}\"', '{\"__echo\": \"str\"}'),
('lvGrow', '#/bin/bash\n\nset -e\n\nvg=${__vgName}\nlv=${__lvName}\ntotSize=${__totSize}\ngrowSize=${__growSize}\ngrow_100=${__grow_100}\n\n# Order of precedence:\n# 1) if grow_100 is true, use lvextend -l +100%FRE device\n# 2) if $totSize is given, use lvextend -L${totSize}G device\n# 3) if $growSize is given, use lvextend -L+${growSize}G device\n\n# Check lv\nif [ ! -b /dev/${vg}/${lv} ]; then\n    echo /dev/${vg}/${lv}\n    exit 31    \nfi\n\nif [ \"$grow_100\" == \"True\" ]; then\n    echo \"lvextend -l +100%FREE /dev/${vg}/${lv}\"   \n    if ! lvextend -l +100%FREE /dev/${vg}/${lv}; then\n        echo \"Error on executing lvextend\" \n    fi\nelif [ $totSize -gt 0 ]; then\n    echo \"lvextend -L${totSize}G /dev/${vg}/${lv}\"\n    if ! lvextend -L${totSize}G /dev/${vg}/${lv}; then\n        echo \"Error on executing lvextend\"\n    fi\nelif [ -n \"$growSize\" ]; then\n    echo \"lvextend -L+${growSize}G /dev/${vg}/${lv}\"\n    if ! lvextend -L+${growSize}G /dev/${vg}/${lv}; then\n        echo \"Error on executing lvextend\"\n    fi\nfi\n\nif file -sL /dev/${vg}/${lv} | grep -Eq \'ext4|ext3|ext2\'; then\n    resize2fs /dev/${vg}/${lv}\nelif file -sL /dev/${vg}/${lv} | grep -iq \'xfs\'; then\n    xfs_growfs /dev/${vg}/${lv}\nelif file -sL /dev/${vg}/${lv} | grep -iq \'btrfs\'; then\n    # A mount point it\'s needed to grow a btrs.\n    mPoint=`mount | grep /dev/${vg}/${lv} | cut -f3 -d \" \"`\n    if [ -z \"$mPoint\" ]; then\n        dmPath=`lvs --noheadings -o lv_dmpath /dev/${vg}/${lv} | tr -d \" \"`\n        mPoint=`mount | grep \"$dmPath\" | cut -f3 -d \" \"`\n    fi\n    if [ -n \"$mPoint\" ]; then\n        echo \"btrfs filesystem resize max $mPoint\"\n        btrfs filesystem resize max $mPoint\n    else\n        echo \"Cannot find mount point for /dev/${vg}/${lv}\"\n    fi\nelse\n    echo \"Can\'t identify the filesystem on the device /dev/${vg}/${lv}, do not grow the filesystem.\"\n    exit 121\nfi', '{\n    \"__vgName\": \"str\",\n    \"__lvName\": \"str\",\n    \"__totSize\": \"int\",\n    \"__growSize\": \"int\",\n    \"__grow_100\": \"bool\"\n}'),
('reboot', '#/bin/bash\n\nreboot', '{}'),
('removeBootstrapKey', '#/bin/bash\n\nset -e\n\npubKey=\"${__pubKey}\"\n\nsed -i -e \"\\|${pubKey}|d\" /root/.ssh/authorized_keys\n', '{}'),
('renameVg', '#/bin/bash\n\nset -e\n\nvg=${__vgName}\n        \n# Get default vg name.\ndefVg=$(vgs --noheadings -o vg_name | tr -d \" \")\necho \"defVg: $defVg\"\necho \"vg: $vg\"\n# Get all lv names.\nlVs=$(lvs --noheadings -o lv_name | tr -d \" \")\n# Get default lv mapper path of the root lv.\ndefRootLvPath=$(grep \" / \" /etc/fstab | cut -f1 -d\" \")\necho \"defRootLvPath: $defRootLvPath\"\n# Pick the lv name of the root lv.\nlvRoot=$(for lv in $lVs;do \n    if grep \" / \" /etc/fstab | grep -q $lv; then \n        echo $lv\n    fi\ndone)\n\n# Swap devices in fstab. Hash: lv[lvname] = /dev/mapper/...\ndeclare -A swapDevs\ndefSwapLvsPath=$(grep \" swap \" /etc/fstab | cut -d\" \" -f1)\n# Map lv path to lv names.\nfor lv in $lVs;do\n    lvPath=$(grep \" swap \" /etc/fstab | grep \"\\-${lv}\" | cut -f1 -d \" \")\n    if [ -n \"$lvPath\" ]; then\n        swapDevs[${lv}]=$lvPath\n    fi\ndone\n# Stop swaps.\nswapoff -a\n\n# Other devices in fstab. Hash: lv[lvname] = /dev/mapper/...\ndeclare -A otherDevs\ndefOtherLvsPath=$(grep -v \' / | swap\' /etc/fstab | grep -E \'ext4|ext3|xfs|brtfs\' | grep -E \"/dev/mapper|/dev/${defVg}\" | cut -d\" \" -f1)\n# Map lv path to lv names, exclude root and swaps.         \nfor lv in $lVs;do\n    lvPath=$(grep -Ev \' / | swap\' /etc/fstab | grep -E \'ext4|ext3|xfs|brtfs\' | grep \"\\-${lv}\" | cut -f1 -d \" \")\n    if [ -n \"$lvPath\" ]; then\n        otherDevs[${lv}]=$lvPath\n    fi\ndone\n         \n# Rename volume group\nif ! vgrename $defVg $vg; then \n    exit 13\nfi\n# Reactivate vg and lvs.\nvgchange -ay || exit 15\nfor lv in $lVs; do \n    if ! lvchange /dev/${vg}/$lv --refresh; then \n        exit 17\n    fi\ndone\n\n# Vg renamed: can get the new lv mapper path of the root lv.\nrootMap=$(lvs --noheadings -o lv_path -S lv_name=$lvRoot | tr -d \" \")\necho \"rootMap: $rootMap\"\n\n# Adjust fstab.\nsed -i -e \"s#${defRootLvPath}#${rootMap}#g\" /etc/fstab # If mapper path was used.\nif [ -n $swapDevs ]; then\n    for lv in \"${!swapDevs[@]}\"; do\n        sed -i -e \"s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/fstab\n    done\nfi\nif [ -n $otherDevs ]; then\n    for lv in \"${!otherDevs[@]}\"; do\n        sed -i -e \"s#${otherDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/fstab\n    done\nfi\nsed -i -e \"s#/${defVg}#/${vg}#g\" /etc/fstab # If /dev/vgname/lvname was used.\n\n# Adjust grub.cfg, grubenv, default-grub. \nfor grubFile in /boot/grub/grub.cfg /boot/grub2/grub.cfg /boot/grub/grubenv /boot/grub2/grubenv /etc/default/grub /etc/sysconfig/grub; do \n    if [ -w $grubFile ]; then\n        sed -i -e \"s#${defRootLvPath}#${rootMap}#g\" $grubFile\n        sed -i -e \"s#/${defVg}#/${vg}#g\" -e \"s#${defVg}/#${vg}/#g\" $grubFile\n    fi\ndone\n    \n# initramfs (adjust swap).\nif [ -w /etc/initramfs-tools/conf.d/resume ]; then\n    for lv in \"${!swapDevs[@]}\"; do\n        sed -i -e \"s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/initramfs-tools/conf.d/resume\n    done\n    sed -i -e \"s#/${defVg}#/${vg}#\" /etc/initramfs-tools/conf.d/resume\nfi\nif [ -x /sbin/update-initramfs ]; then\n    echo \"Rebuilding initrd.\"\n    if ! update-initramfs -u; then \n        exit 19\n    fi\nfi\nif [ -x /sbin/dracut ]; then\n    echo \"Rebuilding initrd.\"\n    dracut --force\nfi\n\nexit 0', '{\n    \"__vgName\": \"str\"\n}'),
('resizeLastPartition', '#/bin/bash\n\nset -e\n\n# Get the number of the last partition and if it\'s an LVM physical volume resize it.\ndev=${__diskDevice}\n\npN=0\npNums=$(grep \" ${dev}[0-9]\" /proc/partitions | awk \'{print $4}\' | sed \"s/${dev}//g\")\nfor n in $pNums; do\n    if [ $n -gt $pN ]; then \n        pN=$n\n    fi\ndone\necho \"Last partition: /dev/${dev}${pN}\"\n    \n# Resize the last partition if it\'s a pv, otherwise skip.\nif pvs /dev/${dev}${pN} > /dev/null 2>&1; then\n    printf \"d\\n${pN}\\nn\\np\\n${pN}\\n\\n\\nt\\n${pN}\\n8e\\nw\\n\" | fdisk /dev/${dev} || true\n    sleep 0.5\n    partprobe /dev/${dev}\n    sleep 1\n    pvresize /dev/${dev}${pN}\nelse\n    echo \"Partition /dev/${dev}${pN} is not a physical volume. Skip it.\" \nfi', '{\n\"__diskDevice\": \"str\"\n}');


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
