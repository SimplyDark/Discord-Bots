import random
from enum import Enum


class GameState(Enum):
    INACTIVE = 0
    ACTIVE = 1


class Game:
    def __init__(self, name, channels):
        self.name = name
        self.players = []
        self.channels = channels
        self.leader = None
        self.ready_players = 12
        self.team_size = int(self.ready_players / 2)
        self.game_state = GameState(0).name
        self.lobby = self.channels[0]
        self.team_1_channel = self.channels[1]
        self.team_2_channel = self.channels[2]

    def get_game_state(self):
        return self.game_state

    def set_game_state(self, num):
        self.game_state = GameState(num).name if num == (0, 1) else None

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players = [user for user in self.players if user.id != player.id]

    def get_player(self, player_id):
        for player in self.players:
            if player_id == player.id:
                return player

    def add_channel(self, channel):
        self.channels.append(channel)

    def set_leader(self, player):
        self.leader = player

    def set_ready_players(self, num):
        self.ready_players = num

    def scramble_players(self):
        team_1_players = 0
        team_2_players = 0
        for player in self.players:
            team = random.randint(1, 2)
            if team == 1 and team_1_players < self.team_size:
                player.set_team(1)
                team_1_players += 1
            elif team == 2 and team_2_players < self.team_size:
                player.set_team(2)
                team_2_players += 1
            elif team == 1 and team_1_players >= self.team_size:
                player.set_team(2)
                team_2_players += 1
            elif team == 2 and team_2_players >= self.team_size:
                player.set_team(1)
                team_1_players += 1
            else:
                print("Something went horribly wrong")

    def sr_scramble_players(self):
        team_1_sr = 0
        team_2_sr = 0
        sr = {}
        for player in self.players:
            sr[player.sr] = player
        sorted_sr = sorted(sr)
        half = int(len(sorted_sr) / 2)
        high_sr = reversed(sorted_sr[half:])
        low_sr = sorted_sr[:half]
        for player in range(int(len(self.players) / 2)):
            if (player % 2) == 0:
                sr[high_sr[player]].set_team(1)
                sr[low_sr[player]].set_team(1)
                team_1_sr += high_sr[player] + low_sr[player]
            else:
                sr[high_sr[player]].set_team(2)
                sr[low_sr[player]].set_team(2)
                team_2_sr += high_sr[player] + low_sr[player]

    def create_teams(self):
        for player in self.players:
            if player.team == 1:
                player.channel = self.channels[1]
                player.set_in_channel()
            else:
                player.channel = self.channels[2]
                player.set_in_channel()

    def average_sr(self):
        num_players = 0
        total_sr = 0
        for player in self.players:
            num_players += 1
            total_sr += player.sr
        return total_sr / num_players

    @staticmethod
    async def move_players_back(game, bot, server, return_channel):
        for player in game.players:
            await bot.move_member(server.get_member(player.id), return_channel)
