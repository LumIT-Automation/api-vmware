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
  `args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`args`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `target_command`
--

CREATE TABLE `target_command` (
  `id_target` int(11) NOT NULL,
  `command` varchar(64) NOT NULL DEFAULT '',
  `args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`args`)),
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
-- Indici per le tabelle `command_launch`
--
ALTER TABLE `target_command`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `command_exec_status`
--
ALTER TABLE `command_exec_status`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ces_command` (`id_command`);


--
-- Indici per le tabelle `command_status`
--


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
  ADD CONSTRAINT `tc_command` FOREIGN KEY (`command`) REFERENCES `command` (`uid`),
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

INSERT INTO `command` (`uid`, `command`, `args`) VALUES
('addPubKey', '#/bin/bash\r\n\r\nset -e\r\n\r\npubKey=${__pubKey}\r\n\r\nif ! grep -q \"${pubKey}\" /root/.ssh/authorized_keys; then echo \"${pubKey}\" >> /root/.ssh/authorized_keys; fi', '{}'),
('addMountPoint', '#/bin/bash\r\n\r\nset -e\r\n\r\nvg=${__vgName}\r\nlv=${__lvName}\r\nsize=${__lvSize}\r\nfolder=${__mountFolder}\r\nfs=${__filesystem}\r\n\r\n# Use /proc to find all processes that have opened file descriptors in the given folder.\r\nfolder_stop_all_processes() {\r\n    if [ -z \"$1\" ]; then\r\n        echo \"Usage: $0 <folder>\"\r\n        exit 0\r\n    fi\r\n    folder=\"$1\"\r\n                    \r\n    echo \"$0: stop all\"\r\n    # Try to stop the processes with a SIGTERM first.\r\n    cd /proc\r\n    for PID in `ls -d [0-9]*`; do \r\n        if ls -l ${PID}/fd 2>/dev/null | grep -q \"$folder\"; then\r\n            if ! ps -up $PID | grep -Eq \"sshd|bash|sudo\"; then \r\n                kill $PID\r\n            fi \r\n        fi\r\n    done\r\n    \r\n    sleep 1\r\n    \r\n    # If SIGTERM is not enough, seng SIGKILL.\r\n    echo \"$0: kill all\"\r\n    cd /proc\r\n    for PID in `ls -d [0-9]*`; do \r\n        if ls -l ${PID}/fd 2>/dev/null | grep -q \"$folder\"; then\r\n            if ! ps -up $PID | grep -Eq \"sshd|bash|sudo\"; then \r\n                kill -9 $PID\r\n            fi \r\n        fi\r\n    done\r\n}\r\n\r\nclone_folder() {\r\n    if [ -z \"$1\" ] || [ -z \"$2\" ]; then\r\n        echo \"Usage: $0 <folder>\"\r\n        exit 0\r\n    fi\r\n    folder=\"$1\"\r\n    dstFolder=\"$2\"\r\n    \r\n    cd $folder || exit 111\r\n    echo \"$0: tar --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar --xattrs --acls xpf -)\"\r\n    tar --xattrs --acls --xattrs-include=* -p -c -f - . | (cd $dstFolder && tar xpf -)\r\n}\r\n\r\ntmpMount=\"\" # Global variable to get the value from tmp_mount() function.\r\ntmp_mount() {\r\n    if [ -z \"$1\" ]; then\r\n        echo \"Usage: $0 <mount_device>\"\r\n        exit 0\r\n    fi\r\n    mountDev=\"$1\"\r\n    mountDir=`mktemp -d`\r\n    echo \"mount $mountDev $mountDir\"\r\n    mount $mountDev $mountDir || exit 121\r\n    tmpMount=$mountDir\r\n}\r\nif ! vgs -o vg_name | grep -q \" ${vg}\"; then\r\n    echo \"Volume group not found.\"\r\n    exit 11\r\nfi\r\nif lvs -o lv_name | grep -q \" $lv \"; then\r\n    echo \"lv $lv already existent\"\r\nelse\r\n    echo \"lvcreate -n $lv -L ${size}G $vg\"\r\n    if ! lvcreate -n $lv -L ${size}G $vg; then\r\n        echo \"can\'t create lv $lv\"\r\n        exit 13\r\n    fi\r\nfi\r\n\r\nif lsblk -n -o FSTYPE /dev/${vg}/${lv} | grep -Eq \'ext[2-4]|xfs|btrfs\'; then\r\n    echo \"lv $lv already formatted\"\r\nelse\r\n    echo \"mkfs.${fs} /dev/${vg}/${lv}\"\r\n    if ! mkfs.${fs} /dev/${vg}/${lv}; then\r\n        echo \"can\'t format /dev/${vg}/${lv}\"\r\n        exit 15\r\n    fi\r\nfi\r\n\r\nif mount  | grep \"$folder\" | grep -E `lvs --noheadings -o lv_dm_path,lv_path /dev/${vg}/${lv} | sed -r -e \'s/^ +//g\' | tr \' \' \'|\'`; then\r\n    echo \"lv $lv already mounted on $folder\"\r\n    # TODO: check lv size here.\r\nelse\r\n    # The folder is already present (but not mounted on $lv), stop processes on it amd move the data.\r\n    if [ -d \"$folder\" ]; then\r\n        folder_stop_all_processes $folder\r\n        tmp_mount \"/dev/${vg}/${lv}\"\r\n        clone_folder $folder $tmpMount\r\n        cd $folder && rm -fr * # cleanup the data in the old place.\r\n        cd\r\n        echo \"umount -l \"/dev/${vg}/${lv}\" && rm -fr $tmpMount\"\r\n        umount -l \"/dev/${vg}/${lv}\" && rm -fr $tmpMount\r\n    else\r\n        mkdir -p $folder || exit 17\r\n    fi\r\n    mount /dev/${vg}/${lv} $folder\r\nfi\r\n          \r\nif ! grep -q \"/dev/${vg}/${lv}\" /etc/fstab; then\r\n    echo \"echo -e \\\"/dev/${vg}/${lv}\\t${folder}\\t$fs\\tdefaults\\t0\\t2\\\" >> /etc/fstab\"    \r\n    echo -e \"/dev/${vg}/${lv}\\t${folder}\\t$fs\\tdefaults\\t0\\t2\" >> /etc/fstab\r\nfi', '{\r\n\"__vgName\": \"str\",\r\n\"__lvName\": \"str\",\r\n\"__lvSize\": \"int\",\r\n\"__mountFolder\": \"str\",\r\n\"__filesystem\": \"str\"\r\n}'),
('echo', '#/bin/bash\r\n\r\nset -e\r\n\r\necho \"${__echo}\"', '{\"__echo\": \"str\"}'),
('lvsGrow', '#/bin/bash\r\n\r\nset -e\r\n\r\nvg=${__vgName}\r\nlv=${__lvName}\r\ntotSize=${__totSize}\r\ngrowSize=${__growSize}\r\ngrow_100=${__grow_100}\r\n\r\n# Order of precedence:\r\n# 1) if grow_100 is true, use lvextend -l +100%FRE device\r\n# 2) if $totSize is given, use lvextend -L${totSize}G device\r\n# 3) if $growSize is given, use lvextend -L+${growSize}G device\r\n\r\n# Check lv\r\nif [ ! -b /dev/${vg}/${lv} ]; then\r\n    echo /dev/${vg}/${lv}\r\n    exit 31    \r\nfi\r\n\r\nif [ \"$grow_100\" == \"True\" ]; then\r\n    echo \"lvextend -l +100%FREE /dev/${vg}/${lv}\"   \r\n    if ! lvextend -l +100%FREE /dev/${vg}/${lv}; then\r\n        echo \"Error on executing lvextend\" \r\n    fi\r\nelif [ $totSize -gt 0 ]; then\r\n    echo \"lvextend -L${totSize}G /dev/${vg}/${lv}\"\r\n    if ! lvextend -L${totSize}G /dev/${vg}/${lv}; then\r\n        echo \"Error on executing lvextend\"\r\n    fi\r\nelif [ -n \"$growSize\" ]; then\r\n    echo \"lvextend -L+${growSize}G /dev/${vg}/${lv}\"\r\n    if ! lvextend -L+${growSize}G /dev/${vg}/${lv}; then\r\n        echo \"Error on executing lvextend\"\r\n    fi\r\nfi\r\n\r\nif file -sL /dev/${vg}/${lv} | grep -Eq \'ext4|ext3|ext2\'; then\r\n    resize2fs /dev/${vg}/${lv}\r\nelif file -sL /dev/${vg}/${lv} | grep -iq \'xfs\'; then\r\n    xfs_growfs /dev/${vg}/${lv}\r\nelif file -sL /dev/${vg}/${lv} | grep -iq \'btrfs\'; then\r\n    # A mount point it\'s needed to grow a btrs.\r\n    mPoint=`mount | grep /dev/${vg}/${lv} | cut -f3 -d \" \"`\r\n    if [ -z \"$mPoint\" ]; then\r\n        dmPath=`lvs --noheadings -o lv_dmpath /dev/${vg}/${lv} | tr -d \" \"`\r\n        mPoint=`mount | grep \"$dmPath\" | cut -f3 -d \" \"`\r\n    fi\r\n    if [ -n \"$mPoint\" ]; then\r\n        echo \"btrfs filesystem resize max $mPoint\"\r\n        btrfs filesystem resize max $mPoint\r\n    else\r\n        echo \"Cannot find mount point for /dev/${vg}/${lv}\"\r\n    fi\r\nelse\r\n    echo \"Can\'t identify the filesystem on the device /dev/${vg}/${lv}, do not grow the filesystem.\"\r\n    exit 121\r\nfi', '{\r\n    \"vgNmae\": \"str\",\r\n    \"lvName\": \"str\",\r\n    \"totSize\": \"int\",\r\n    \"growSize\": \"int\",\r\n    \"grow_100\": \"bool\"\r\n}'),
('reboot', '#/bin/bash\r\n\r\nreboot', '{}'),
('removeBootstrapKey', '#/bin/bash\r\n\r\nset -e\r\n\r\npubKey=\"${__pubKey}\"\r\n\r\nsed -i -e \'|${pubKey}|d\' /root/.ssh/authorized_keys\r\n', '{}'),
('renameVg', '#/bin/bash\r\n\r\nset -e\r\n\r\nvg={__vgName}\r\n        \r\n# Get default vg name.\r\ndefVg=$(vgs --noheadings -o vg_name | tr -d \" \")\r\necho \"defVg: $defVg\"\r\necho \"vg: $vg\"\r\n# Get all lv names.\r\nlVs=$(lvs --noheadings -o lv_name | tr -d \" \")\r\n# Get default lv mapper path of the root lv.\r\ndefRootLvPath=$(grep \" / \" /etc/fstab | cut -f1 -d\" \")\r\necho \"defRootLvPath: $defRootLvPath\"\r\n# Pick the lv name of the root lv.\r\nlvRoot=$(for lv in $lVs;do \r\n    if grep \" / \" /etc/fstab | grep -q $lv; then \r\n        echo $lv\r\n    fi\r\ndone)\r\n\r\n# Swap devices in fstab. Hash: lv[lvname] = /dev/mapper/...\r\ndeclare -A swapDevs\r\ndefSwapLvsPath=$(grep \" swap \" /etc/fstab | cut -d\" \" -f1)\r\n# Map lv path to lv names.\r\nfor lv in $lVs;do\r\n    lvPath=$(grep \" swap \" /etc/fstab | grep \"\\-${lv}\" | cut -f1 -d \" \")\r\n    if [ -n \"$lvPath\" ]; then\r\n        swapDevs[${lv}]=$lvPath\r\n    fi\r\ndone\r\n# Stop swaps.\r\nfor dev in $defSwapLvsPath; do \r\n    swapoff $dev\r\ndone\r\n\r\n# Other devices in fstab. Hash: lv[lvname] = /dev/mapper/...\r\ndeclare -A otherDevs\r\ndefOtherLvsPath=$(grep -v \' / | swap\' /etc/fstab | grep -E \'ext4|ext3|xfs|brtfs\' | grep -E \"/dev/mapper|/dev/${defVg}\" | cut -d\" \" -f1)\r\n# Map lv path to lv names, exclude root and swaps.         \r\nfor lv in $lVs;do\r\n    lvPath=$(grep -Ev \' / | swap\' /etc/fstab | grep -E \'ext4|ext3|xfs|brtfs\' | grep \"\\-${lv}\" | cut -f1 -d \" \")\r\n    if [ -n \"$lvPath\" ]; then\r\n        otherDevs[${lv}]=$lvPath\r\n    fi\r\ndone\r\n         \r\n# Rename volume group\r\nif ! vgrename $defVg $vg; then \r\n    exit 13\r\nfi\r\n# Reactivate vg and lvs.\r\nvgchange -ay || exit 15\r\nfor lv in $lVs; do \r\n    if ! lvchange /dev/${vg}/$lv --refresh; then \r\n        exit 17\r\n    fi\r\ndone\r\n\r\n# Vg renamed: can get the new lv mapper path of the root lv.\r\nrootMap=$(lvs --noheadings -o lv_path -S lv_name=$lvRoot | tr -d \" \")\r\necho \"rootMap: $rootMap\"\r\n\r\n# Adjust fstab.\r\nsed -i -e \"s#${defRootLvPath}#${rootMap}#g\" /etc/fstab # If mapper path was used.\r\nif [ -n $swapDevs ]; then\r\n    for lv in \"${!swapDevs[@]}\"; do\r\n        sed -i -e \"s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/fstab\r\n    done\r\nfi\r\nif [ -n $otherDevs ]; then\r\n    for lv in \"${!otherDevs[@]}\"; do\r\n        sed -i -e \"s#${otherDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/fstab\r\n    done\r\nfi\r\nsed -i -e \"s#/${defVg}#/${vg}#g\" /etc/fstab # If /dev/vgname/lvname was used.\r\n\r\n# Adjust grub.cfg, grubenv, default-grub. \r\nfor grubFile in /boot/grub/grub.cfg /boot/grub2/grub.cfg /boot/grub/grubenv /boot/grub2/grubenv /etc/default/grub /etc/sysconfig/grub; do \r\n    if [ -w $grubFile ]; then\r\n        sed -i -e \"s#${defRootLvPath}#${rootMap}#g\" $grubFile\r\n        sed -i -e \"s#/${defVg}#/${vg}#g\" -e \"s#${defVg}/#${vg}/#g\" $grubFile\r\n    fi\r\ndone\r\n    \r\n# initramfs (adjust swap).\r\nif [ -w /etc/initramfs-tools/conf.d/resume ]; then\r\n    for lv in \"${!swapDevs[@]}\"; do\r\n        sed -i -e \"s#${swapDevs[$lv]}#/dev/${vg}/${lv}#g\" /etc/initramfs-tools/conf.d/resume\r\n    done\r\n    sed -i -e \"s#/${defVg}#/${vg}#\" /etc/initramfs-tools/conf.d/resume\r\nfi\r\nif [ -x /sbin/update-initramfs ]; then\r\n    echo \"Rebuilding initrd.\"\r\n    if ! update-initramfs -u; then \r\n        exit 19\r\n    fi\r\nfi\r\nif [ -x /sbin/dracut ]; then\r\n    echo \"Rebuilding initrd.\"\r\n    dracut --force\r\nfi\r\n\r\nexit 0', '{\r\n    \"__vgName\": \"str\"\r\n}'),
('resizeLastPartition', '#/bin/bash\r\n\r\nset -e\r\n\r\n# Get the number of the last partition and if it\'s an LVM physical volume resize it.\r\ndev=${__diskDevice}\r\n\r\npN=0\r\npNums=$(grep \" ${dev}[0-9]\" /proc/partitions | awk \'{print $4}\' | sed \"s/${dev}//g\")\r\nfor n in $pNums; do\r\n    if [ $n -gt $pN ]; then \r\n        pN=$n\r\n    fi\r\ndone\r\necho \"Last partition: /dev/${dev}${pN}\"\r\n    \r\n# Resize the last partition if it\'s a pv, otherwise skip.\r\nif pvs /dev/${dev}${pN} > /dev/null 2>&1; then\r\n    printf \"d\\n${pN}\\nn\\np\\n${pN}\\n\\n\\nt\\n${pN}\\n8e\\nw\\n\" | fdisk /dev/${dev} || true\r\n    sleep 0.5\r\n    partprobe /dev/${dev}\r\n    sleep 1\r\n    pvresize /dev/${dev}${pN}\r\nelse\r\n    echo \"Partition /dev/${dev}${pN} is not a physical volume. Skip it.\" \r\nfi', '{\r\n\"__diskDevice\": \"str\"\r\n}');


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
