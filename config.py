import configparser
import os


class Config:
    def __init__(self, file):
        self.file = os.path.dirname(os.path.realpath(__file__)) + "/" + file
        config = configparser.ConfigParser()

        config.read_file(open(self.file))

        self.token = config.get("Credentials", "Token")
        self.server = config.get("Server", "Server")
        self.default_channel = config.get("Server", "Default Channel")
        self.message_channel = config.get("Server", "Message Channel")
