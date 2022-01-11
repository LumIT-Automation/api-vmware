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
-- Database: `api`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `asset`
--

CREATE TABLE `asset` (
  `id` int(11) NOT NULL,
  `address` varchar(64) NOT NULL,
  `port` int(11) DEFAULT NULL,
  `fqdn` varchar(255) DEFAULT NULL,
  `baseurl` varchar(255) NOT NULL,
  `tlsverify` tinyint(4) NOT NULL DEFAULT 1,
  `datacenter` varchar(255) DEFAULT NULL,
  `environment` varchar(255) NOT NULL,
  `position` varchar(255) DEFAULT NULL,
  `api_type` varchar(64) NOT NULL DEFAULT '',
  `api_additional_data` varchar(255) NOT NULL DEFAULT '',
  `username` varchar(64) NOT NULL DEFAULT '',
  `password` varchar(64) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `group_role_object`
--

CREATE TABLE `group_role_object` (
  `id` int(255) NOT NULL,
  `id_group` int(11) NOT NULL,
  `id_role` int(11) NOT NULL,
  `id_object` varchar(64) NOT NULL,
    `id_asset` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `identity_group`
--

CREATE TABLE `identity_group` (
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `identity_group_identifier` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `log`
--

CREATE TABLE `log` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `action` varchar(255) NOT NULL,
  `asset_id` int(11) NOT NULL,
  `config_object_type` varchar(255) NOT NULL,
  `config_object` varchar(255) NOT NULL,
  `status` varchar(32) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `migrations`
--

CREATE TABLE `migrations` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `vmObject`
--

CREATE TABLE `vmObject` (
  `moId` varchar(64) NOT NULL,
  `id_asset` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `privilege`
--

CREATE TABLE `privilege` (
  `id` int(11) NOT NULL,
  `privilege` varchar(64) NOT NULL,
  `privilege_type` enum('object','asset','global') NOT NULL DEFAULT 'object',
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `role`
--

CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `role` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `role_privilege`
--

CREATE TABLE `role_privilege` (
  `id_role` int(11) NOT NULL,
  `id_privilege` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `asset`
--
ALTER TABLE `asset`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `address` (`address`);

--
-- Indici per le tabelle `group_role_object`
--
ALTER TABLE `group_role_object`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `identity_group`
--
ALTER TABLE `identity_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `identity_group_identifier` (`identity_group_identifier`) USING BTREE,
  ADD KEY `name` (`name`);

--
-- Indici per le tabelle `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `username` (`username`);

--
-- Indici per le tabelle `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `vmObject`
--
ALTER TABLE `vmObject`
  ADD PRIMARY KEY (`moId`,`id_asset`),
  ADD KEY `name` (`name`),
  ADD KEY `p_asset` (`id_asset`);

--
-- Indici per le tabelle `privilege`
--
ALTER TABLE `privilege`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `privilege` (`privilege`);

--
-- Indici per le tabelle `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `role` (`role`);

--
-- Indici per le tabelle `role_privilege`
--
ALTER TABLE `role_privilege`
  ADD PRIMARY KEY (`id_role`,`id_privilege`),
  ADD KEY `rp_privilege` (`id_privilege`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `asset`
--
ALTER TABLE `asset`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `group_role_object`
--
ALTER TABLE `group_role_object`
  MODIFY `id` int(255) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `identity_group`
--
ALTER TABLE `identity_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `log`
--
ALTER TABLE `log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `privilege`
--
ALTER TABLE `privilege`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `role`
--
ALTER TABLE `role`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `group_role_object`
--
ALTER TABLE `group_role_object`
  ADD CONSTRAINT `gro_group` FOREIGN KEY (`id_group`) REFERENCES `identity_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `gro_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `gro_assetObject` FOREIGN KEY (`id_object`,`id_asset`) REFERENCES `vmObject` (`moId`,`id_asset`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `vmObject`
--
ALTER TABLE `vmObject`
  ADD CONSTRAINT `p_asset` FOREIGN KEY (`id_asset`) REFERENCES `asset` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `role_privilege`
--
ALTER TABLE `role_privilege`
  ADD CONSTRAINT `rp_privilege` FOREIGN KEY (`id_privilege`) REFERENCES `privilege` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `rp_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;