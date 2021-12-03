from django.urls import path

from .controllers import Root
from .controllers.VMware import Datacenters, Datacenter
from .controllers.VMware import Clusters, Cluster
from .controllers.VMware import Datastore
from .controllers.VMware import VMFolders, VMFolder
from .controllers.VMware.Asset import Asset, Assets
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions, VMFolders as PermissionVMFolders, VMFolder as PermissionVMFolder
from .controllers import History


urlpatterns = [
    path('', Root.RootController.as_view()),

    path('identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view(), name='permission-identity-groups'),
    path('identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view(), name='permission-identity-group'),
    path('roles/', Roles.PermissionRolesController.as_view(), name='permission-roles'),
    path('permissions/', Permissions.PermissionsController.as_view(), name='permissions'),
    path('permission/<int:permissionId>/', Permission.PermissionController.as_view(), name='permission'),
    path('permissions/vmFolders/', PermissionVMFolders.PermissionVMFoldersController.as_view(), name='permissions-vmfolders'),
    path('permissions/vmFolder/<int:assetId>/<str:moId>/', PermissionVMFolder.PermissionVMFolderController.as_view(), name='permissions-vmfolder'),

    path('authorizations/', Authorizations.AuthorizationsController.as_view(), name='authorizations'),

    # Asset.
    path('assets/', Assets.VMwareAssetsController.as_view(), name='vmware-assets'),
    path('asset/<int:assetId>/', Asset.VMwareAssetController.as_view(), name='vmware-asset'),

    # Datacenter.
    path('<int:assetId>/datacenters/', Datacenters.VMwareDatacentersController.as_view(), name='vmware-datacenters'),
    path('<int:assetId>/datacenter/<str:moId>/', Datacenter.VMwareDatacenterController.as_view(), name='vmware-datacenter'),

    # Cluster.
    path('<int:assetId>/clusters/', Clusters.VMwareClustersController.as_view(), name='vmware-clusters'),
    path('<int:assetId>/cluster/<str:moId>/', Cluster.VMwareClusterController.as_view(), name='vmware-cluster'),

    # Datastore.
#    path('<int:assetId>/datastores/', Clusters.VMwareClustersController.as_view(), name='vmware-datastores'),
    path('<int:assetId>/datastore/<str:moId>/', Datastore.VMwareDatastoreController.as_view(), name='vmware-datastore'),

    # VMFolder.
    path('<int:assetId>/vmFolders/', VMFolders.VMwareVMFoldersController.as_view(), name='vmware-vmFolders'),
    path('<int:assetId>/vmFolder/<str:moId>/', VMFolder.VMwareVMFolderController.as_view(), name='vmware-vmFolder'),

    # Log history.
    path('history/', History.HistoryLogsController.as_view(), name='vmware-log-history'),
]
