import discord
import asyncio
import random
from discord.ext.commands import Bot

cmd_prefix = "!"
bot = Bot(command_prefix=cmd_prefix)
server_id = "330465109900132352"  # 324996864115998730
channel_id = "330465109900132353"  # 332666054276939776
games = {}  # Game contains channels, leader, and players
ready_players = 12
authorized = "Idiot"


@bot.event
async def on_ready():
    await bot.send_message(bot.get_channel("330465109900132352"), "is online")


# Commands
@bot.command(brief="Displays version")
async def version():
    await bot.say("Pre-alpha 1")


@bot.command(brief="Announces phrases, please wrap in quotes")
async def announce(message):
    if message == "pug":
        await bot.say("@everyone PUG about to start. Type \"!join pug\" to join")
    else:
        await bot.say(message)


@bot.command(pass_context=True, brief="Starts a game")
async def start(game):
    global user_id, server, return_channel, user
    command = cmd_prefix + str(game.command) + " "
    user_id = game.message.author.id
    server = bot.get_server(server_id)
    return_channel = bot.get_channel(channel_id)
    user = server.get_member(user_id)
    game_id = game.message.content.replace(command, '')
    if authorized in [i.name for i in user.roles]:  # Check if user is authorized (in the role) to use this command
        if game.message.content.startswith(command + game_id):
            # Create PUG channels
            lobby = await bot.create_channel(server, "[" + game_id + "] " + "Lobby", type=discord.ChannelType.voice)
            team_1_channel = await bot.create_channel(server, "[" + game_id + "] " + "Team 1", type=discord.ChannelType.voice)
            team_2_channel = await bot.create_channel(server, "[" + game_id + "] " + "Team 2", type=discord.ChannelType.voice)
            global game_active
            game_active = 0
            channels = [lobby, team_1_channel, team_2_channel]
            # Create PUG leader and assign permissions
            pug_leader = await bot.create_role(server, name="PUG Leader", hoist=1, color=discord.Color.blue())
            await bot.add_roles(game.message.author, pug_leader)
            permissions = discord.PermissionOverwrite()
            # Permissions
            permissions.move_members = True
            # Adds channels and leader to game
            games[game_id] = [channels, pug_leader, {}]
            for channel in channels:
                await bot.edit_channel_permissions(channel, pug_leader, permissions)
            await bot.send_message(game.message.channel, "PUG started")


@bot.command(brief="Sets the amount of players in a game")
async def set_players(players):
    global ready_players
    ready_players = players


@bot.command(pass_context=True, brief="Ends a game")
async def end(game):
    command = cmd_prefix + str(game.command) + " "
    game_id = str(game.message.content.replace(command, ''))
    if game_id in list(games.keys()):
        if games[game_id][1] in game.message.author.roles:  # Check if message is sent by PUG leader
            # Move players back before the PUG channels get deleted
            try:
                await move_players_back(games[game_id][2])
            except IndexError:
                pass
            # Delete PUG channels
            await bot.delete_channel(games[game_id][0][0])
            await bot.delete_channel(games[game_id][0][1])
            await bot.delete_channel(games[game_id][0][2])
            await bot.delete_role(server, games[game_id][1])
            del games[game_id]
            await bot.send_message(game.message.channel, "PUG ended")


@bot.command(pass_context=True, brief="Readies up player")
async def ready(ctx):
    # Set player to ready
    user = ctx.message.author
    player_id = ctx.message.author.id
    game_id = get_user_game(user)
    if await get_user_channel(user) in games[game_id][0]:
        player_ids = games[game_id][2]
        games[game_id][2][player_id] = [user, "ready", 0]
        team_1_channel = games[game_id][0][1]
        team_2_channel = games[game_id][0][2]
        ready_num = 0
        # Count the amount of players ready
        for player in range(len(player_ids)):
            if "ready" in str(list(player_ids.values())[player][1]):
                ready_num += 1
        # If the number of ready people matches this number then start the lobby in 5 seconds
        if int(ready_num) == int(ready_players):
            global game_active
            game_active = 1
            seconds = 5
            start_message = "Everyone has readied up, lobby starting in {} seconds"
            start_time = await bot.send_message(ctx.message.channel, start_message.format(seconds))
            for i in range(seconds):
                await asyncio.sleep(1)
                seconds -= 1
                await bot.edit_message(start_time, start_message.format(seconds))
            await bot.delete_message(start_time)
            # Create and scramble teams
            scramble_teams = scramble(player_ids, 6) # works
            teams = create_teams(player_ids, scramble_teams, team_1_channel, team_2_channel)
            players = list(teams.keys())
            channels = list(teams.values())
            for player in range(len(players)):
                # For some reason, discord only checks the amount of channel members when it is created.
                # So this is my hack to manually add them to the channel
                if channels[player] == team_1_channel:
                    team_1_channel.voice_members.append(server.get_member(players[player]))
                else:
                    team_2_channel.voice_members.append(server.get_member(players[player]))
                # Move players to their team's voice channel
                await bot.move_member(server.get_member(players[player]), channels[player])


@bot.command(pass_context=True, brief="Joins a game")
async def join(game):
    command = cmd_prefix + str(game.command) + " "
    player = server.get_member(game.message.author.id)
    player_id = game.message.author.id
    game_id = str(game.message.content.replace(command, ''))
    lobby = games[game_id][0][0]
    if game.message.content.startswith(command + game_id):
        if check_players(12, lobby):
            # list order: [name, ready status, in team channel]
            games[game_id][2][player_id] = [player, 0, 0]
            await bot.move_member(player, lobby)
            if user not in lobby.voice_members:
                lobby.voice_members.append(player)
        else:
            await bot.send_message(game.message.channel, "Sorry, PUG is full")
            print(lobby.voice_members)


@bot.command(pass_context=True, brief="Leave a game")
async def leave(ctx):
    user = ctx.message.author
    player_id = ctx.message.author.id
    game_id = get_user_game(user)
    if get_user_channel(user) in games[game_id][0]:
        del games[game_id][2][player_id]


@bot.command(pass_context=True)
async def remove(member):
    user = member.message.author
    game_id = get_user_game(user)
    player = server.get_member_named(member)
    if get_user_channel(user) in games[game_id][0] and games[game_id][1] in user.roles:
        del games[game_id][2][player.id]
        await bot.move_member(return_channel, player)


@bot.command(pass_context=True, brief="Restart a game")
async def restart(game):
    command = cmd_prefix + str(game.command) + " "
    user = game.message.author
    game_id = str(game.message.content.replace(command, ''))
    lobby = games[game_id][0][0]
    if games[game_id][1] in user.roles:
        for player in list(games[game_id][2].keys()):
            games[game_id][2][player] = [server.get_member(player), 0, 0]
            await bot.move_member(server.get_member(player), lobby)


@bot.command(pass_context=True, brief="Displays the status of a game")
async def status(game):
    command = cmd_prefix + str(game.command) + " "
    game_id = str(game.message.content.replace(command, ''))
    if game.message.content.startswith(command + game_id):
        try:
            if game_active == 0:
                await bot.send_message(game.message.channel, "{} players waiting for a PUG".format(len(games[game_id][0][0].voice_members)))
            elif game_active == 1:
                total_players = len(games[game_id][0][1].voice_members) + len(games[game_id][0][2].voice_members)
                await bot.send_message(game.message.channel, "{} players are in a PUG".format(total_players))
        except (NameError, KeyError):
            await bot.send_message(game.message.channel, "Game does not exist...")


@bot.command(pass_context=True, brief="Lists the games in progress")
async def list_games(ctx):
    games_list = await bot.send_message(ctx.message.channel, "Games in progress: \n")
    game_list = []
    for game in list(games.keys()):
        game_list.append(str(game) + "\n")
    await bot.edit_message(games_list, "Games in progress: \n" + ''.join(game_list))


@bot.command(pass_context=True, hidden=True)
async def debug(ctx):
    print(games)
    get_user_channel(ctx.message.author)
    get_user_game(ctx.message.author)
    print([i.name for i in ctx.message.author.roles])


async def move_players_back(players):
    # Make sure all the players are not in PUG voice channels before deleting them
    for player in list(players.keys()):
        await bot.move_member(server.get_member(player), return_channel)


async def get_user_channel(user):
    channels = bot.get_all_channels()
    for channel in channels:
        if user in channel.voice_members:
            return channel


def get_user_game(user):
    for game in games.items():
        game_name = game[0]
        for channel in game[1][0]:
            if user in channel.voice_members:
                return game_name
            else:
                print("This happened")


def scramble(players, team_size):
    team_1 = [1]
    team_2 = [2]
    tmp = players.copy()
    for player in tmp.keys():
        team = random.randint(0, 1)
        if team == 0 and len(team_1) < team_size:
            team_1.append(player)
        elif team == 1 and len(team_2) < team_size:
            team_2.append(player)
        else:
            print("This should not happen")
    return team_1, team_2


def create_teams(players, teams, channel_1, channel_2):
    team_members = {}
    for team in teams:
        if team[0] == 1:
            team_channel = channel_1
        else:
            team_channel = channel_2
        for player in team[1:]: # First index of array is the team id
            if players[player][2] == 0:
                players[player][2] = 1 # Set player to already joined team channel
                team_members[player] = team_channel
            else:
                print("Player tried to move but wasn't allowed to")
    return team_members


def check_players(number, channel):
    if len(channel.voice_members) < number:
        return True
    else:
        return False

# Bot token (¿Bot?)
bot.run("MzMwNDY0MDM4MTA0NDY1NDA4.DDhcUQ.g7XglufF0DJCow_nm0MoKyUW53Q")
