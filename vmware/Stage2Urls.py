from django.urls import path

from .controllers import Root
from .controllers.Stage2 import BoostrapKeys, BoostrapKey, Targets, Target, Command, Commands, RunCommand, TargetCommands, TargetCommand, FinalPubKeys, FinalPubKey


urlpatterns = [
    path('', Root.RootController.as_view()),

    # SSH keys.
    path('bootstrapkeys/', BoostrapKeys.Stage2BootstrapKeysController.as_view(), name='stage2-bootstrap-keys'),
    path('bootstrapkey/<int:keyId>/', BoostrapKey.Stage2BootstrapKeyController.as_view(), name='stage2-bootstrap-key'),

    # Commands.
    path('commands/', Commands.Stage2CommandsController.as_view(), name='stage2-commands'),
    path('command/<str:commandUid>/', Command.Stage2CommandController.as_view(), name='stage2-command'),

    # Targets (virtualmachines to be processed).
    path('targets/', Targets.Stage2TargetsController.as_view(), name='stage2-targets'),
    path('target/<int:targetId>/', Target.Stage2TargetController.as_view(), name='stage2-target'),

    # Target commands.
    path('target/<int:targetId>/command/<str:commandUid>/', TargetCommand.Stage2TargetCommandController.as_view(), name='stage2-target-command'),
    path('target/<int:targetId>/commands/', TargetCommands.Stage2TargetCommandsController.as_view(), name='stage2-target-commands'),

    # Final public keys.
    path('finalpubkeys/', FinalPubKeys.Stage2FinalPubKeysController.as_view(), name='stage2-final-pub-keys'),
    path('finalpubkey/<int:keyId>/', FinalPubKey.Stage2FinalPubKeyController.as_view(), name='stage2-final-pub-key'),

    # Virtual machine commands.
    path('command/<str:commandUid>/run/<int:targetId>/', RunCommand.Stage2CommandRunController.as_view(), name='stage2-command-run'),
    path('command/<str:commandUid>/run/<int:targetId>/<int:pubKeyId>/', RunCommand.Stage2CommandRunController.as_view(), name='stage2-command-run-pubkey'),
]
