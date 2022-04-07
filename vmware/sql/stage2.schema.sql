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
  `id` int(11) NOT NULL,
  `id_target` int(11) NOT NULL,
  `command` varchar(64) NOT NULL DEFAULT '',
  `args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (JSON_VALID(args))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `command_exec_status`
--

CREATE TABLE `command_exec_status` (
  `id` int(11) NOT NULL,
  `id_command` int(11) NOT NULL,
  `exec_count` tinyint NOT NULL,
  `exit_status` int(11) NOT NULL,
  `stdout` varchar(65536) NOT NULL DEFAULT '',
  `stderr` varchar(65536) NOT NULL DEFAULT ''
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
-- Indici per le tabelle `command_status`
--
ALTER TABLE `command_exec_status`
  ADD PRIMARY KEY (`id`);


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
-- AUTO_INCREMENT per la tabella `target_command`
--
ALTER TABLE `target_command`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `command_exec-status`
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
  ADD CONSTRAINT `tg_key` FOREIGN KEY (`id_target`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `command_exec_status`
--
ALTER TABLE `command_exec_status`
  ADD CONSTRAINT `cmd_key` FOREIGN KEY (`id_command`) REFERENCES `target_command` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;


-- --------------------------------------------------------

--
-- Dump dei dati per la tabella `command`
--

INSERT INTO `command` (`uid`, `command`, `args`) VALUES
('ResizeLastPartition', 'set -e\r\n\r\n# Get the number of the last partition and if it\'s an LVM physical volume resize it.\r\ndev={diskDevice}\r\n\r\npN=0\r\npNums=$(grep \" ${dev}[0-9]\" /proc/partitions | awk \'{print $4}\' | sed \"s/${dev}//g\")\r\nfor n in $pNums; do\r\n    if [ $n -gt $pN ]; then \r\n        pN=$n\r\n    fi\r\ndone\r\necho \"Last partition: /dev/${dev}${pN}\"\r\n    \r\n# Resize the last partition if it\'s a pv, otherwise skip.\r\nif pvs /dev/${dev}${pN} > /dev/null 2>&1; then\r\n    printf \"d\\n${pN}\\nn\\np\\n${pN}\\n\\n\\nt\\n${pN}\\n8e\\nw\\n\" | fdisk /dev/${dev} || true\r\n    sleep 0.5\r\n    partprobe /dev/${dev}\r\n    sleep 1\r\n    pvresize /dev/${dev}${pN}\r\nelse\r\n    echo \"Partition /dev/${dev}${pN} is not a physical volume. Skip it.\" \r\nfi', '{\r\n\"diskDevice\": \"str\"\r\n}');


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
