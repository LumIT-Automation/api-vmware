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
  `ip` varchar(63) NOT NULL,
  `port` int(11) DEFAULT NULL,
  `api_type` varchar(63) NOT NULL DEFAULT '',
  `id_bootstrap_key` INT DEFAULT NULL,
  `username` varchar(63) NOT NULL DEFAULT '',
  `password` varchar(63) NOT NULL DEFAULT '',
  `id_asset` int(11) DEFAULT NULL,
  `task_moid` varchar(63) DEFAULT NULL,
  `task_status` varchar(63) NOT NULL DEFAULT 'undefined',
  `vm_name` varchar(127) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `bootstrap_key`
--

CREATE TABLE `bootstrap_key` (
  `id` int(11) NOT NULL,
  `priv_key` varchar(8192) NOT NULL DEFAULT '',
  `comment` varchar(1024) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `group_pubkey`
--

CREATE TABLE `final_pubkey` (
  `id` int(11) NOT NULL,
  `comment` varchar(1024) NOT NULL,
  `pubkey` varchar(2048) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `group_pubkey`
--

CREATE TABLE `target_final_pubkey` (
  `id_target` int(11) NOT NULL,
  `id_pubkey` int(11) NOT NULL
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
-- Indici per le tabelle `group_pubkey`
--
ALTER TABLE `target_final_pubkey`
  ADD PRIMARY KEY `id_final_pubkey` (`id_target`, `id_pubkey`);

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
-- AUTO_INCREMENT per la tabella `group_pubkey`
--
ALTER TABLE `final_pubkey`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `stage2_target`
--
ALTER TABLE `target`
  ADD CONSTRAINT `bk_key` FOREIGN KEY (`id_bootstrap_key`) REFERENCES `bootstrap_key` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `stage2_target`
--
ALTER TABLE `target_final_pubkey`
  ADD CONSTRAINT `tg_id_target` FOREIGN KEY (`id_target`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tg_id_pubkey` FOREIGN KEY (`id_pubkey`) REFERENCES `final_pubkey` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
