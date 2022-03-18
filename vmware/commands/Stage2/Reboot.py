
from vmware.commands.Stage2.SshCommand import SshCommand


class Reboot(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        self.command = 'reboot'

