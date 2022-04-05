
from vmware.commands.Stage2.SshCommand import SshCommand
from vmware.models.Stage2.FinalPubKey import FinalPubKey


class TargetAddFinalPubKey(SshCommand):
    def __init__(self, targetId: int, keyId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        pubKey = FinalPubKey(keyId).pub_key
        self.command = "if ! grep -q \"" + pubKey + "\" /root/.ssh/authorized_keys; then echo \"" + pubKey + "\" >> /root/.ssh/authorized_keys; fi"