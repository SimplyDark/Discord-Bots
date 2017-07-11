import discord


class Player:
    def __init__(self, member, bot):
        self.id = member.id
        self.name = member.name
        self.ready = "Not ready"
        self.in_channel = "Not in channel"
        self.channel = None
        self.team_channel = None
        self.team = -1
        self.bot = bot
        self.sr = 0

    def set_ready(self):
        self.ready = "Ready"

    def set_in_channel(self):
        self.in_channel = "In channel"

    def set_sr(self, num):
        self.sr = num

    def get_ready(self):
        return self.ready

    def get_channel(self):
        in_channel = None
        for channel in self.bot.get_all_channels():
            user = discord.utils.get(channel.voice_members, name=self.name)
            if user is not None:
                in_channel = channel
                break
        return in_channel

    def get_game(self, games):
        for game in list(games.values()):
            if self.get_channel() in game.channels:
                return game.name

    def set_team(self, team):
        self.team = team if team in (1, 2) else print(str(team) + " is not a valid team")

    def update(self, game):
        game.remove_player(self)
        game.add_player(self)


