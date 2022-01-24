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
(1, '192.168.12.8', NULL, 'vcsa.lumitlab.local', 'https://vcsa.lumitlab.local/', 0, 'Milano', 'Development', 'RACK 1', 'vmware', '', 'administrator@vsphere.local', 'Password01!!');

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


INSERT INTO `privilege` (`id`, `privilege`, `privilege_type`, `description`) VALUES
(1, 'asset_patch', 'asset', NULL),
(2, 'asset_delete', 'asset', NULL),
(3, 'assets_get', 'asset', NULL),
(4, 'assets_post', 'asset', NULL),
(5, 'permission_identityGroups_get', 'global', NULL),
(6, 'permission_identityGroups_post', 'global', NULL),
(7, 'permission_roles_get', 'global', NULL),
(8, 'permission_identityGroup_patch', 'global', NULL),
(9, 'permission_identityGroup_delete', 'global', NULL),
(10, 'permission_vmfolders_get', 'global', NULL),
(11, 'permission_vmfolder_delete', 'global', NULL),
(12, 'datacenters_get', 'asset', NULL),
(13, 'datacenter_get', 'asset', NULL),
(14, 'clusters_get', 'asset', NULL),
(15, 'cluster_get', 'asset', NULL),
(16, 'hostsystems_get', 'asset', NULL),
(17, 'hostsystem_get', 'asset', NULL),
(18, 'datastores_get', 'asset', NULL),
(19, 'datastore_get', 'object', NULL),
(20, 'networks_get', 'asset', NULL),
(21, 'network_get', 'object', NULL),
(22, 'folder_get', 'object', NULL),
(23, 'folders_get', 'object', NULL),
(24, 'virtualmachines_get', 'asset', NULL),
(25, 'virtualmachine_get', 'asset', NULL),
(26, 'templates_get', 'asset', NULL),
(27, 'template_get', 'asset', NULL),
(28, 'template_post', 'asset', NULL),
(29, 'custom_specs_get', 'asset', NULL),
(30, 'custom_specs_post', 'asset', NULL),
(31, 'custom_spec_get', 'asset', NULL),
(32, 'custom_spec_delete', 'asset', NULL),
(33, 'custom_spec_patch', 'asset', NULL),
(34, 'historyComplete_get', 'global', NULL);


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
(1, 16),
(1, 17),
(1, 18),
(1, 19),
(1, 20),
(1, 21),
(1, 22),
(1, 23),
(1, 24),
(1, 25),
(1, 26),
(1, 27),
(1, 28),
(1, 29),
(1, 30),
(1, 31),
(1, 32),
(1, 33),
(1, 34),
(2, 3),
(2, 12),
(2, 13),
(2, 14),
(2, 15),
(2, 16),
(2, 17),
(2, 18),
(2, 19),
(2, 20),
(2, 21),
(2, 22),
(2, 23),
(2, 24),
(2, 25),
(2, 26),
(2, 27),
(2, 28),
(2, 29),
(2, 30),
(2, 31),
(2, 32),
(2, 33),
(3, 3),
(3, 19),
(3, 21),
(3, 22),
(3, 23),
(3, 24),
(3, 25),
(3, 26),
(3, 27),
(3, 28),
(3, 29),
(3, 30),
(3, 31),
(3, 32),
(3, 33);

--
--
-- Dump dei dati per la tabella `vmware_object`
--

INSERT INTO `vmware_object` (`id`, `moId`, `id_asset`, `name`, `description`) VALUES
(1, 'any', 1, 'any', 'All the objects of this vCenter'),
(2, 'group-v2477', 1, 'rrivarie', ''),
(3, 'datastore-2341', 1, 'NFS_Datastore', ''),
(4, 'network-1213', 1, 'LumitLab_18', '');


--
-- Dump dei dati per la tabella `group_role_object`
--

INSERT INTO `group_role_object` (`id`, `id_group`, `id_role`, `id_object`) VALUES
(1, 1, 1, 1),
(3, 2, 2, 2),
(4, 2, 3, 3),
(5, 3, 3, 4);



COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
