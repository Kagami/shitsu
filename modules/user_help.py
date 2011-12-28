import utils


def main(bot, args):
    """help
    Help.
    See also: man
    """
    if not args:
        return utils.trim("""
            Type %lsmod to show avialable modules.
            Type %man <module> to show module's help.
            Sources and bug tracker: https://github.com/Kagami/C.C.
            """)
