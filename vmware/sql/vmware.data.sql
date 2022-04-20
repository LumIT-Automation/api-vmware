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
(18, 'datastores_get', 'object-datastore', NULL),
(19, 'datastore_get', 'object-datastore', NULL),
(20, 'networks_get', 'object-network', NULL),
(21, 'network_get', 'object-network', NULL),
(22, 'folder_get', 'object-folder', NULL),
(23, 'folders_get', 'object-folder', NULL),
(24, 'folders_tree_get', 'object-folder', NULL),
(25, 'virtualmachines_get', 'asset', NULL),
(26, 'virtualmachine_get', 'asset', NULL),
(27, 'templates_get', 'asset', NULL),
(28, 'template_get', 'asset', NULL),
(29, 'template_post', 'asset', NULL),
(30, 'custom_specs_get', 'asset', NULL),
(31, 'custom_specs_post', 'asset', NULL),
(32, 'custom_spec_get', 'asset', NULL),
(33, 'custom_spec_delete', 'asset', NULL),
(34, 'custom_spec_patch', 'asset', NULL),
(35, 'historyComplete_get', 'global', NULL),
(36, 'target_commands_get', 'global', NULL),
(37, 'target_command_delete', 'global', NULL),
(38, 'target_commands_post', 'global', NULL),
(39, 'task_get', 'asset', NULL),
(40, 'task_delete', 'asset', NULL),
(41, 'task_patch', 'asset', NULL),
(42, 'virtualmachine_patch', 'asset', NULL),
(43, 'vm_guestos_patch', 'asset', NULL),
(44, 'bootstrap_keys_get', 'global', NULL),
(45, 'bootstrap_key_delete', 'global', NULL),
(46, 'bootstrap_key_patch', 'global', NULL),
(47, 'bootstrap_key_post', 'global', NULL),
(48, 'final_pub_keys_get', 'global', NULL),
(49, 'final_pub_key_delete', 'global', NULL),
(50, 'final_pub_key_patch', 'global', NULL),
(51, 'final_pub_key_post', 'global', NULL),
(52, 'commands_get', 'global', NULL),
(53, 'commands_post', 'global', NULL),
(54, 'command_get', 'global', NULL),
(55, 'command_delete', 'global', NULL),
(56, 'command_patch', 'global', NULL),
(57, 'commandrun_put', 'global', NULL),
(58, 'targets_get', 'global', NULL),
(59, 'target_get', 'global', NULL),
(60, 'target_delete', 'global', NULL),
(61, 'target_patch', 'global', NULL),
(62, 'target_post', 'global', NULL);


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
(1, 3),
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
(1, 35),
(1, 36),
(1, 37),
(1, 38),
(1, 39),
(1, 40),
(1, 41),
(1, 42),
(1, 43),
(1, 44),
(1, 45),
(1, 46),
(1, 47),
(1, 48),
(1, 49),
(1, 50),
(1, 51),
(1, 52),
(1, 53),
(1, 54),
(1, 55),
(1, 56),
(1, 57),
(1, 58),
(1, 59),
(1, 60),
(1, 61),
(1, 62),
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
(2, 34),
(2, 36),
(2, 39),
(2, 42),
(2, 43),
(2, 44),
(2, 48),
(2, 52),
(2, 54),
(2, 57),
(2, 58),
(2, 59),
(3, 3),
(3, 12),
(3, 13),
(3, 14),
(3, 15),
(3, 16),
(3, 17),
(3, 18),
(3, 19),
(3, 20),
(3, 21),
(3, 22),
(3, 23),
(3, 24),
(3, 25),
(3, 26),
(3, 27),
(3, 28),
(3, 30),
(3, 32),
(3, 36),
(3, 39),
(3, 44),
(3, 48),
(3, 52),
(3, 54),
(3, 58),
(3, 59);


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
