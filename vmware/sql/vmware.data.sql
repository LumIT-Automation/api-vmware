-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Mag 06, 2021 alle 16:58
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

--
-- Dump dei dati per la tabella `asset`
--

INSERT INTO `asset` (`id`, `address`, `port`, `fqdn`, `baseurl`, `tlsverify`, `datacenter`, `environment`, `position`, `api_type`, `api_additional_data`, `username`, `password`) VALUES
(1, '192.168.12.8', NULL, 'vcsa.lumitlab.local', 'https://vcsa.lumitlab.local/', 0, 'Milano', 'Development', 'RACK 1', 'Vmware', '', 'administrator@vsphere.local', 'Password01!!');

--
-- Dump dei dati per la tabella `identity_group`
--

INSERT INTO `identity_group` (`id`, `name`, `identity_group_identifier`) VALUES
(1, 'groupAdmin', 'cn=groupadmin,cn=users,dc=lab,dc=local'),
(2, 'groupStaff', 'cn=groupstaff,cn=users,dc=lab,dc=local'),
(3, 'groupReadOnly', 'cn=groupreadonly,cn=users,dc=lab,dc=local');

--
-- Dump dei dati per la tabella `privilege`
--

INSERT INTO `privilege` (`id`, `privilege`, `description`) VALUES
(1, 'asset_patch', NULL),
(2, 'asset_delete', NULL),
(3, 'assets_get', NULL),
(4, 'assets_post', NULL),
(5, 'permission_identityGroups_get', NULL),
(6, 'permission_identityGroups_post', NULL),
(7, 'permission_roles_get', NULL),
(8, 'permission_identityGroup_patch', NULL),
(9, 'permission_identityGroup_delete', NULL),
(10, 'vmFolders_get', NULL),
(11, 'folder_get', NULL),
(12, 'folders_get', NULL),
(13, 'node_patch', NULL),
(14, 'node_delete', NULL),
(15, 'historyComplete_get', NULL);


--
-- Dump dei dati per la tabella `role`
--

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly');

--
-- Dump dei dati per la tabella `role_privilege`
--

INSERT INTO `role_privilege` (`id_role`, `id_privilege`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(1, 9),
(1, 10),
(1, 11),
(1, 12),
(1, 13),
(1, 14),
(1, 15),
(2, 3),
(2, 10),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(2, 15),
(3, 3),
(3, 10),
(3, 11);


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
