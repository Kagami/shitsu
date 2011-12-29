import modules
import utils


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        return utils.trim("""
            Type %lsmod to show avialable modules.
            Type %man <module> to show module's help.
            Sources and bug tracker: https://github.com/Kagami/C.C.
            """)
