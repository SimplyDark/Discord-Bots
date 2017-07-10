import discord
import asyncio
import os
import sys
from discord.ext.commands import Bot

from player import Player
from game import Game
from server_switcher import ServerSwitcher
from pug_logger import PugLogger
from updater import update

logger = PugLogger()

cmd_prefix = "!"
bot = Bot(command_prefix=cmd_prefix)
server_switch = ServerSwitcher()
server_id = server_switch.servers[0]
default_channel = server_switch.default_channels[0]
message_channel = server_switch.message_channels[0]
master = "328965253314379778"
games = {}  # Contains Game objects
authorized = "Pug Leader"


@bot.event
async def on_ready():
    await bot.send_message(bot.get_channel(message_channel), "is online")
    logger.log.info(bot.user.name + " has logged into server " + bot.get_server(server_id).name)


# Commands
@bot.command(brief="Displays version")
async def version():
    await bot.say("Pre-alpha 2.5")


@bot.command(pass_context=True, brief="Announces phrases, please wrap in quotes")
async def announce(ctx):
    command = cmd_prefix + str(ctx.command) + " "
    msg = ctx.message.content.replace(command, '', 1)
    if msg == "pug":
        await bot.say("@everyone PUG about to start. Type \"!join pug\" to join")
    else:
        await bot.say(msg)
        logger.log.info(ctx.message.author.name + " announced \"" + msg + "\"")


@bot.command(pass_context=True, brief="Sets the amount of players in a game")
async def set_players(ctx):
    args = str(ctx.message.content).split()
    try:
        game_name = args[1]
        players = args[2]
        game = games[game_name]
        if game_name == str(game.name):
            game.ready_players = int(players)
            game.team_size = int(game.ready_players / 2)
    except IndexError:
        await bot.send_message(ctx.message.author, "Incorrect amount of arguments")


@bot.command(pass_context=True, brief="Starts a game")
async def start(ctx):
    global return_channel, server, pug_leader
    user = ctx.message.author
    command = cmd_prefix + str(ctx.command) + " "
    game_name = ctx.message.content.replace(command, '')
    server = bot.get_server(server_id)
    return_channel = bot.get_channel(default_channel)
    if authorized in [role.name for role in user.roles]:
        leader_color = discord.Color.blue()
        lobby = await bot.create_channel(server, "[" + game_name + "] " + "Lobby", type=discord.ChannelType.voice)
        team_1_channel = await bot.create_channel(server, "[" + game_name + "] " + "Team 1", type=discord.ChannelType.voice)
        team_2_channel = await bot.create_channel(server, "[" + game_name + "] " + "Team 2", type=discord.ChannelType.voice)
        pug_leader = await bot.create_role(server, name="PUG Leader", hoist=1, color=leader_color)
        game = Game(name=game_name, channels=[lobby, team_1_channel, team_2_channel])
        game.set_leader(user)
        games[game.name] = game
        await bot.add_roles(user, pug_leader)
        await bot.send_message(ctx.message.channel, "PUG started")
        logger.log.info(user.name + " started pug \"{}\"".format(game_name))
    else:
        await bot.send_message(user, "Sorry, you are not authorized to use this command")
        logger.log.info("Unauthorized user " + user.name + " tried to start a pug called \"{}\"".format(game_name))


@bot.command(pass_context=True, brief="Joins a game")
async def join(ctx):
    user = ctx.message.author
    command = cmd_prefix + str(ctx.command) + " "
    game_name = str(ctx.message.content.replace(command, ''))
    player = Player(user, bot)
    try:
        lobby = games[game_name].channels[0]
        if len(lobby.voice_members) < 12:
            games[game_name].add_player(player)
            await bot.move_member(user, lobby)
            if user not in lobby.voice_members:
                lobby.voice_members.append(user)
        else:
            await bot.send_message(user, "Sorry, PUG is full")
    except KeyError:
        logger.log.info(user.name + " tried to join nonexistent game \"{}\"".format(game_name))


@bot.command(pass_context=True, brief="Readies up player")
async def ready(ctx):
    user = ctx.message.author
    player = Player(user, bot)
    game_name = player.get_game(games)
    game = games[game_name]
    try:
        ready_num = 0
        player.set_ready()
        player.update(game)
        for member in games[game_name].players:
            if "Ready" == member.ready:
                ready_num += 1
        if int(ready_num) == int(game.ready_players):
            game.set_game_state(1)
            seconds = 5
            start_message = "Everyone has readied up, lobby starting in {} seconds."
            message = await bot.send_message(ctx.message.channel, start_message.format(seconds))
            for i in range(seconds):
                await asyncio.sleep(1)
                seconds -= 1
                await bot.edit_message(message, start_message.format(seconds))
            await bot.delete_message(message)
            game.scramble_players()
            game.create_teams()
            for member in game.players:
                team_member = server.get_member(member.id)
                if member.team == 1:
                    game.channels[1].voice_members.append(team_member)
                else:
                    game.channels[2].voice_members.append(team_member)
                game.lobby.voice_members = [member for i in game.lobby.voice_members if i.id != member.id]
                await bot.move_member(team_member, member.channel)
    except KeyError:
        logger.log.info(user.name + " tried to ready in  nonexistent game")


@bot.command(pass_context=True, hidden=True)
async def transfer(player):
    user = player.message.author
    command = cmd_prefix + str(player.command) + " "
    player_name = str(player.message.content.replace(command, ''))
    recipient = server.get_member_named(player_name)
    old_leader = Player(user, bot)
    game_name = old_leader.get_game(games)
    game = games[game_name]
    if user is game.leader:
        game.set_leader(recipient)
        await bot.add_roles(recipient, pug_leader)
        await bot.remove_roles(user, pug_leader)
        await bot.send_message(player.message.channel, "Leadership of game \"{}\" transferred from {} to {}".format(game_name, user.name, player_name))
    else:
        logger.log.info(user.name + " tried to transfer leadership while not leader")

@bot.command(pass_context=True, brief="Leave a game")
async def leave(ctx):
    user = ctx.message.author
    command = cmd_prefix + str(ctx.command) + " "
    game_name = str(ctx.message.content.replace(command, ''))
    game = games[game_name]
    player = game.get_player(user.id)
    if player.get_channel() in game.channels and game:
        game.remove_player(player)
        await bot.send_message(user, "You have been removed from the game: \"" + game.name + "\"")


@bot.command(pass_context=True, hidden=True)
async def remove(member):
    user = member.message.author
    command = cmd_prefix + str(member.command) + " "
    game_name = str(member.message.content.replace(command, ''))
    game = games[game_name]
    kick = game.get_player(server.get_member_named(member).id)
    if kick.get_channel() in game.channels and game.leader is user and game:
        game.remove_player(kick)
        await bot.move_member(return_channel, kick)
        logger.log.info(kick.name + " was kicked from game \"{}\" by {}".format(game_name, user.name))


@bot.command(pass_context=True, brief="Ends a game")
async def end(ctx):
    user = ctx.message.author
    command = cmd_prefix + str(ctx.command) + " "
    game_name = str(ctx.message.content.replace(command, ''))
    game = games[game_name]
    if game and game.leader is user:
        for player in game.players:
            await bot.move_member(server.get_member(player.id), return_channel)
        for channel in game.channels:
            await bot.delete_channel(channel)
        del games[game_name]
        await bot.delete_role(server, pug_leader)
        await bot.send_message(ctx.message.channel, "PUG ended")
        logger.log.info(user.name + " ended game \"{}\"".format(game_name))
    else:
        logger.log.info("Unauthorized user {} tried to end game \"{}\"".format(user.name, game_name))


@bot.command(pass_context=True, brief="Restart a game")
async def restart(ctx):
    user = ctx.message.author
    command = cmd_prefix + str(ctx.command) + " "
    game_name = str(ctx.message.content.replace(command, ''))
    game = games[game_name]
    lobby = game.channels[0]
    if game.leader is user:
        for player in game.players:
            player.ready = "Not ready"
            player.in_channel = "Not in channel"
            player.update(game)
            await bot.move_member(server.get_member(player.id), lobby)
        logger.log.info(user.name + " restarted game \"{}\"".format(game_name))
    else:
        logger.log.info("Unauthorized user {} tried to restart game \"{}\"".format(user.name, game_name))


@bot.command(pass_context=True, brief="Displays the status of a game")
async def status(ctx):
    command = cmd_prefix + str(ctx.command) + " "
    game_name = str(ctx.message.content.replace(command, ''))
    try:
        game = games[game_name]
        if game.get_game_state() == "INACTIVE":
            await bot.send_message(ctx.message.channel, "{} players waiting for a PUG".format(len(game.lobby.voice_members)))
        elif game.get_game_state() == "ACTIVE":
            total_players = len(game.team_1_channel.voice_members) + len(game.team_2_channel.voice_members)
            await bot.send_message(ctx.message.channel, "{} players are in a PUG".format(total_players))
    except (NameError, KeyError):
        await bot.send_message(ctx.message.channel, "Game does not exist...")


@bot.command(pass_context=True, brief="Lists the games in progress")
async def list_games(ctx):
    games_list = await bot.send_message(ctx.message.channel, "Games in progress: \n")
    game_list = []
    for game in list(games.keys()):
        game_list.append(str(game) + "\n")
    if not game_list:
        await bot.edit_message(games_list, "Games in progress: \n" + "None")
    else:
        await bot.edit_message(games_list, "Games in progress: \n" + ''.join(game_list))


@bot.command(pass_context=True, hidden=True)
async def fanfare(link):
    args = str(link.message.content).split()
    user = link.message.author
    player = Player(user, bot)
    if user.id == master:
        try:
            if args[1].startswith("http") and bot not in player.get_channel().voice_members:
                global voice, noise
                voice = await bot.join_voice_channel(player.get_channel())
                noise = await voice.create_ytdl_player(args[1])
                noise.start()
            elif args[1].startswith("http"):
                noise = await voice.create_ytdl_player(args[1])
                noise.start()
            if args[1] == "stop" and noise:
                noise.stop()
                voice.disconnect()
        except IndexError:
            print("No args")
    else:
        logger.log.info("Someone.... {} tried to be you...".format(user.name))


@bot.command(pass_context=True, hidden=True)
async def debug(ctx):
    print("Nothing for now")
    print(__file__)
    print(sys.argv)
    print(sys.executable)


# Do not run in IDE if you want to test this
@bot.command(pass_context=True, hidden=True)
async def restart_bot(ctx):
    user = ctx.message.author
    if user.id == master:
        logger.log.info("Bot {} has been restarted".format(bot.user.name))
        os.execv(sys.executable, [sys.executable] + sys.argv)


@bot.command(hidden=True)
async def who():
    await bot.say("I am " + bot.user.name)


@bot.command(pass_context=True, hidden=True)
async def update_bot(ctx):
    user = ctx.message.author
    if user.id == master:
        update()
        os.execv(sys.executable, [sys.executable] + sys.argv)


# Bot token (¿Bot?)
# bot.run("MzMwNDY0MDM4MTA0NDY1NDA4.DDhcUQ.g7XglufF0DJCow_nm0MoKyUW53Q")

# Bot token (¿Simple?)
bot.run("MzMzMjczMzgxOTI1NTUyMTI4.DEKQkA.WqC_45xC_g8y3Gicd8jI5gsjl_M")