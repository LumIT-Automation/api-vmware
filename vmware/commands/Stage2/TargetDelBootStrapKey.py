
from vmware.models.Stage2.Target import Target
from vmware.commands.Stage2.SshCommand import SshCommand


class TargetDelBootstrapKey(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        target = Target(targetId)
        pubKey = target.getBootstrapPubKey()
        self.command = "sed -i -e '\|" + pubKey + "|d' /root/.ssh/authorized_keys"
