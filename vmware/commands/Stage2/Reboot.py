import time

from vmware.commands.Stage2.SshCommand import SshCommand
from vmware.helpers.Exception import CustomException


class RebootCommand(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        self.command = 'reboot'
        self.alwaysSuccess = True



class TestConnect(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)

        self.command = 'echo'



class Reboot:
    def __init__(self, targetId: int, checkInterval: int = 5, maxChecks: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targetId = int(targetId)
        if checkInterval < 2:
            raise CustomException(status=400, payload={"Ssh": "Error: checkInterval minimum value is 2."})
        self.checkInterval = checkInterval
        self.maxChecks = maxChecks



    def exec(self, data: dict = None) -> None:
        data = {} if data is None else data
        reboot = RebootCommand(targetId=self.targetId)
        reboot.exec(data=data)

        tcpTimeout = self.checkInterval - 1
        tests = 0
        while tests < self.maxChecks:
            time.sleep(self.checkInterval)
            test = TestConnect(targetId=self.targetId)
            try:
                test.exec(tcpTimeout=tcpTimeout)
                return
            except Exception:
                pass
            tests += 1

        raise CustomException(status=504, payload={"Ssh": "Wait for power on: timeout exceeded."})




