from shitsu import modules
import datetime


class Date(modules.MessageModule):

    args = (0,)

    def run(self):
        """
        Show current date and time.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
