import logging
import datetime
import os


class PugLogger:
    def __init__(self):
        self.log = logging.getLogger("[PUG Bot]")
        self.log.setLevel(logging.INFO)

        current_time = datetime.datetime.now()
        date = datetime.datetime.strftime(current_time, "%m-%d-%y")
        time = datetime.datetime.strftime(current_time, "%I:%M:%S %p")

        parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
        try:
            handler = logging.FileHandler(parent_dir + "Logs/[PUG Bot] " + date + ".log")
        except FileNotFoundError:
            os.makedirs("Logs")
            handler = logging.FileHandler(parent_dir + "Logs/[PUG Bot] " + date + ".log")
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt="{} [%(levelname)s] %(name)s %(message)s".format(time))
        handler.setFormatter(formatter)

        self.log.addHandler(handler)
