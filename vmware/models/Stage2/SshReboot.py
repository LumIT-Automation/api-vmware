
from vmware.models.Stage2.SshCommand import SshCommand


class SshReboot(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        self.command = '/bin/echo \"Puongiorno\"'

