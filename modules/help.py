import modules


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        return self.get_utils().trim("""
            Type %lsmod to show avialable modules.
            Type %man <module> to show module's help.
            Sources and bug tracker: https://github.com/Kagami/C.C.
            """)
