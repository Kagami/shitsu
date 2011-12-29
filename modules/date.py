import modules
import datetime


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        """date
        Show current date and time.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
