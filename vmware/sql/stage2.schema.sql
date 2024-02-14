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
  `second_stage_state` varchar(32) DEFAULT NULL DEFAULT '',
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
  `template_args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`template_args`)),
  `reserved` tinyint(4) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `target_command`
--

CREATE TABLE `target_command` (
  `id` int(11) NOT NULL,
  `id_target` int(11) NOT NULL,
  `command` varchar(64) NOT NULL DEFAULT '',
  `user_args` varchar(8192) NOT NULL DEFAULT '{}' CHECK (json_valid(`user_args`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `target_command_exec`
--

CREATE TABLE `target_command_exec` (
  `id` int(11) NOT NULL,
  `id_target_command` int(11) NOT NULL,
  `timestamp` datetime(4) NOT NULL DEFAULT current_timestamp(4),
  `exit_status` int(11) NOT NULL,
  `stdout` mediumtext DEFAULT NULL,
  `stderr` mediumtext DEFAULT NULL
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
-- Indici per le tabelle `target_command_exec`
--
ALTER TABLE `target_command_exec`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ces_command` (`id_target_command`);

--
-- Indici per le tabelle `target_command`
--
ALTER TABLE `target_command`
  ADD PRIMARY KEY (`id`),
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
-- AUTO_INCREMENT per la tabella `target_command`
--
ALTER TABLE `target_command`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `target_command_exec`
--
ALTER TABLE `target_command_exec`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;


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
-- Limiti per la tabella `target_command_exec`
--
ALTER TABLE `target_command_exec`
  ADD CONSTRAINT `tc_exec` FOREIGN KEY (`id_target_command`) REFERENCES `target_command` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
