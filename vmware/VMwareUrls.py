from django.urls import path

from .controllers import Root, RawTxtController
from .controllers.VMware import Datacenters, Datacenter
from .controllers.VMware import Clusters, Cluster
from .controllers.VMware import HostSystems, HostSystem
from .controllers.VMware import Datastores, Datastore
from .controllers.VMware import Networks,Network
from .controllers.VMware import NetworkVMs, FindUsedIp
from .controllers.VMware import VMFolders, VMFolder, VMFoldersTree
from .controllers.VMware import VirtualMachines, VirtualMachine
from .controllers.VMware import VMGuestOS
from .controllers.VMware import Templates, Template
from .controllers.VMware import Task, Tasks
from .controllers.VMware import CustomSpecs, CustomSpec
from .controllers.VMware.Asset import Asset, Assets
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions, VObjects as PermissionVMObjects, VObject as PermissionVMObject
from .controllers import History


urlpatterns = [
    path('', Root.RootController.as_view()),

    path('identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view(), name='permission-identity-groups'),
    path('identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view(), name='permission-identity-group'),
    path('roles/', Roles.PermissionRolesController.as_view(), name='permission-roles'),
    path('permissions/', Permissions.PermissionsController.as_view(), name='permissions'),
    path('permission/<int:permissionId>/', Permission.PermissionController.as_view(), name='permission'),
    path('permissions/vmObjects/', PermissionVMObjects.PermissionVObjectsController.as_view(), name='permissions-vmobject'),
    path('permissions/vmObject/<int:objectId>/', PermissionVMObject.PermissionVObjectController.as_view(), name='permissions-vmobject'),

    path('authorizations/', Authorizations.AuthorizationsController.as_view(), name='authorizations'),

    path('doc/<str:fileName>/', RawTxtController.VMwareRawTxtController.as_view(), name='txt'),

    # Asset.
    path('assets/', Assets.VMwareAssetsController.as_view(), name='vmware-assets'),
    path('asset/<int:assetId>/', Asset.VMwareAssetController.as_view(), name='vmware-asset'),

    # Datacenter.
    path('<int:assetId>/datacenters/', Datacenters.VMwareDatacentersController.as_view(), name='vmware-datacenters'),
    path('<int:assetId>/datacenter/<str:moId>/', Datacenter.VMwareDatacenterController.as_view(), name='vmware-datacenter'),

    # Cluster.
    path('<int:assetId>/clusters/', Clusters.VMwareClustersController.as_view(), name='vmware-clusters'),
    path('<int:assetId>/cluster/<str:moId>/', Cluster.VMwareClusterController.as_view(), name='vmware-cluster'),

    # HostSystems.
    path('<int:assetId>/hostsystems/', HostSystems.VMwareHostSystemsController.as_view(), name='vmware-clusters'),
    path('<int:assetId>/hostsystem/<str:moId>/', HostSystem.VMwareHostSystemController.as_view(), name='vmware-clusters'),

    # Datastore.
    path('<int:assetId>/datastores/', Datastores.VMwareDatastoresController.as_view(), name='vmware-datastores'),
    path('<int:assetId>/datastore/<str:moId>/', Datastore.VMwareDatastoreController.as_view(), name='vmware-datastore'),

    # Network.
    path('<int:assetId>/networks/', Networks.VMwareNetworksController.as_view(), name='vmware-networks'),
    path('<int:assetId>/network/<str:moId>/', Network.VMwareNetworkController.as_view(), name='vmware-network'),
    path('<int:assetId>/network/<str:moId>/vms/', NetworkVMs.VMwareNetworkVMsController.as_view(), name='vmware-network'),
    path('<int:assetId>/network/<str:moId>/find-ip/<str:ipAddress>/', FindUsedIp.VMwareNetworkFindIpController.as_view(), name='vmware-network-find-ip'),

    # VMFolder.
    path('<int:assetId>/vmFolders/', VMFolders.VMwareVMFoldersController.as_view(), name='vmware-vmFolders'),
    path('<int:assetId>/vmFolders/tree/', VMFoldersTree.VMwareVMFoldersTreeController.as_view(), name='vmware-vmFolders-tree'),
    path('<int:assetId>/vmFolder/<str:moId>/', VMFolder.VMwareVMFolderController.as_view(), name='vmware-vmFolder'),
    path('<int:assetId>/vmFolder/<str:moId>/parentList/', VMFolder.VMwareVMFolderParentListController.as_view(), name='vmware-vmFolder-parentlist'),

    # VirtualMachine.
    path('<int:assetId>/virtualmachines/', VirtualMachines.VMwareVirtualMachinesController.as_view(), name='vmware-virtualmachines'),
    path('<int:assetId>/virtualmachine/<str:moId>/', VirtualMachine.VMwareVirtualMachineController.as_view(), name='vmware-virtualmachine'),
    path('<int:assetId>/virtualmachine/<str:moId>/guestos/', VMGuestOS.VMwareVirtualMachineGuestOSController.as_view(), name='vmware-virtualmachine-guestos'),

    path('<int:assetId>/templates/', Templates.VMwareTemplatesController.as_view(), name='vmware-templates'),
    path('<int:assetId>/template/<str:moId>/', Template.VMwareVirtualMachineTemplateController.as_view(), name='vmware-template'),

    path('<int:assetId>/task/<str:moId>/', Task.VMwareTaskController.as_view(), name='vmware-task'),
    path('<int:assetId>/tasks/', Tasks.VMwareTasksController.as_view(), name='vmware-tasks'),

    # Virtual machines customization specifications.
    path('<int:assetId>/customSpecs/', CustomSpecs.VMwareCustomSpecsController.as_view(), name='vmware-customSpecs'),
    path('<int:assetId>/customSpec/<str:specName>/', CustomSpec.VMwareCustomSpecController.as_view(), name='vmware-customSpec'),

    # Log history.
    path('history/', History.HistoryLogsController.as_view(), name='vmware-log-history'),
]
