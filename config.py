import configparser


class Config:
    def __init__(self, file):
        self.file = file
        config = configparser.ConfigParser()

        config.read(file, encoding="utf-8")

        self.token = config.get("Credentials", "Token")
        self.server = config.get("Server", "Server")
        self.default_channel = config.get("Server", "Default Channel")
        self.message_channel = config.get("Server", "Message Channel")
