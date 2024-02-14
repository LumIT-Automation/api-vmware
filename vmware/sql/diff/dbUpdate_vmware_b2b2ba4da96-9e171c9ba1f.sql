
/*
OLD COMMIT: b2b2ba4da96bef265552f319be13747cb38fcf2a
NEW COMMIT: 9e171c9ba1f0db327ba43cbe1be941195b2306a1
*/


/*
SQL SCHEMA SECTION
*/

## mysqldiff 0.60
## 
## Run on Wed Feb 14 15:37:43 2024
## Options: debug=0, host=10.0.111.25, user=api, password=password
##
## --- file: /tmp/vmware_old.sql
## +++ file: /tmp/vmware_new.sql

ALTER TABLE asset CHANGE COLUMN baseurl baseurl varchar(255) NOT NULL DEFAULT ''; # was varchar(255) NOT NULL
ALTER TABLE asset CHANGE COLUMN fqdn fqdn varchar(255) NOT NULL; # was varchar(255) DEFAULT NULL
ALTER TABLE asset DROP INDEX address; # was UNIQUE (address)
ALTER TABLE asset DROP COLUMN address; # was varchar(64) NOT NULL
ALTER TABLE asset ADD COLUMN protocol varchar(16) NOT NULL DEFAULT 'https' AFTER fqdn;
ALTER TABLE asset ADD COLUMN port int(11) NOT NULL DEFAULT 443 AFTER protocol;
ALTER TABLE asset CHANGE COLUMN port port int(11) NOT NULL DEFAULT 443 AFTER protocol; # was int(11) DEFAULT NULL
ALTER TABLE asset DROP COLUMN api_additional_data; # was varchar(255) NOT NULL DEFAULT ''
ALTER TABLE asset DROP COLUMN api_type; # was varchar(64) NOT NULL DEFAULT ''
ALTER TABLE asset ADD COLUMN path varchar(255) NOT NULL DEFAULT '/' AFTER port;
ALTER TABLE asset MODIFY `tlsverify` tinyint(4) NOT NULL DEFAULT 1 AFTER path;

ALTER TABLE asset ADD UNIQUE fqdn (fqdn,protocol,port);


/*
DATA SECTION
*/

set foreign_key_checks = 0;

# Set the protocol from the original baseurl.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.protocol = SUBSTRING_INDEX(A2.baseurl,':',1);

# select if(p0 REGEXP '.*/$', p0, concat(p0, '/') ) as path from (select REGEXP_REPLACE(A2.baseurl, '[a-zA-Z]+://[0-9a-zA-Z.-]+(:[0-9]+)?(/.*)', '\\2') as p0 from A2) as p1;

# Set the path from the original baseurl.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.path = (select if(p0 REGEXP '.*/$', p0, concat(p0, '/') ) from (select REGEXP_REPLACE(A3.baseurl, '[a-zA-Z]+://[0-9a-zA-Z.-]+(:[0-9]+)?(/.*)', '\\2') as p0 from asset A3) as p1);

# Put an "/" at the end of the baseurl if missing.
update asset A1 INNER JOIN asset A2 ON A1.id = A2.id set A1.baseurl = ( select if(b0 REGEXP '.*/$', b0, concat(b0, '/') ) as b from (select A3.baseurl as b0 from asset A3) as a );



truncate table privilege;
truncate table role_privilege;
truncate table role;


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
(62, 'target_post', 'global', NULL),
(63, 'full_visibility', 'global', NULL);

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
(1, 63),
(2, 3),
(2, 12),
(2, 13),
(2, 15),
(2, 24),
(2, 27),
(2, 28),
(2, 29),
(2, 30),
(2, 31),
(2, 44),
(2, 48),
(2, 58),
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
(3, 59),
(4, 3);

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly'),
(4, 'workflow', 'workflow system user');


set foreign_key_checks = 1;
