from django.urls import path

from .controllers import Root
from .controllers.Stage2 import Targets, Target
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions, VMObjects as PermissionVMObjects, VMObject as PermissionVMObject
from .controllers import History


urlpatterns = [
    path('', Root.RootController.as_view()),

    # Targets (virtualmachines to be processed)
    path('targets/', Targets.Stage2TargetsController.as_view(), name='stage2-targets'),
    path('stage2/target/<int:targetId>/', Target.Stage2TargetController.as_view(), name='stage2-target'),

]
