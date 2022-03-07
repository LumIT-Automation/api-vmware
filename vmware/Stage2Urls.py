from django.urls import path

from .controllers import Root
from .controllers.Stage2 import Targets, Target
from .controllers.Stage2 import BoostrapKeys, BoostrapKey


urlpatterns = [
    path('', Root.RootController.as_view()),

    # Targets (virtualmachines to be processed)
    path('bootstrapkeys/', BoostrapKeys.Stage2BootstrapKeysController.as_view(), name='stage2-bootstrap-keys'),
    path('bootstrapkey/<int:keyId>/', BoostrapKey.Stage2BootstrapKeyController.as_view(), name='stage2-bootstrap-key'),

    # Targets (virtualmachines to be processed)
    path('targets/', Targets.Stage2TargetsController.as_view(), name='stage2-targets'),
    path('target/<int:targetId>/', Target.Stage2TargetController.as_view(), name='stage2-target'),

]
