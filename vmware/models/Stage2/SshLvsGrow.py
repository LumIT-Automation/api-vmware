
from vmware.models.Stage2.SshCommand import SshCommand


class SshLvsGrow(SshCommand):
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(targetId, *args, **kwargs)


        """ 
        Vars expected from the http PUT:
        "shellVars" = {
            "vgNmae": "vg0",
            "lvName": "lv_name",
            "totSize": 10,
            "growSize": 2,
            "grow_100": False
        }
        """

        # Variables passed to the shell script via shellVars.
        self.shellVars = """
            vg={vgName}
            lv={lvName}
            totSize={totSize}
            growSize={growSize}
            grow_100={grow_100}
        """



        self.command = """
            # Check lv
            if [ ! -b /dev/${vg}/${lv} ]; then
                echo /dev/${vg}/${lv}
                exit 31    
            fi

            if [ "$grow_100" == "true" ]; then            
                lvextend -l +100%FREE /dev/${vg}/${lv}
            elif [ -n "$totSize" ]; then
                lvextend -L${totSize}G /dev/${vg}/${lv}
            elif [ -n "$growSize" ]; then
                lvextend -L+${growSize}G /dev/${vg}/${lv}
            fi

        """
