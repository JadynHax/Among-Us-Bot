#!/usr/bin/env python

"""
    Among Us Discord Bot - Main bot file.
    Copyright (C) 2020  Jason Rutz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord, os, asyncio
from discord.ext import commands
from utils import load_yaml, dump_yaml
from checks import is_bot_owner


# Code to run at startup
if not os.path.exists("prefixes.yml"):
    dump_yaml({"global": "a!", "guild": {}, "user": {}}, "prefixes.yml")

# Load prefixes
bot_prefixes = load_yaml("prefixes.yml")
print(bot_prefixes)

config = load_yaml("config.yml")

# Gets possible prefixes to use
async def prefix_callable(bot, message):
    guild = message.guild
    prefix_results = []
    if guild:
        if str(guild.id) in bot_prefixes["guild"].keys():
            prefix_results.append(bot_prefixes["guild"][str(guild.id)])

        else:
            prefix_results.append(bot_prefixes["global"])

    else:
        prefix_results.append(bot_prefixes["global"])

    if str(message.author.id) in bot_prefixes["user"].keys():
        prefix_results.append(bot_prefixes["user"][str(message.author.id)])

    return commands.when_mentioned_or(*prefix_results)(bot, message)


# Initiate bot with members intent set to True
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix=prefix_callable,
    description="A bot made to mimic the way Among Us is played—but on Discord! Has many memes, too.",
    intents=intents,
    case_insensitive=True,
)
bot.bot_prefixes = bot_prefixes

# Custom exceptions for error definitions
class NotImpostorError(Exception):
    def __init__(self, ctx, message=None):
        if message is None:
            message = f"You are not an Impostor! You can't run **{bot.command_prefix(bot, ctx.message)}{ctx.command}**!\n**Tip:** your goal is to complete all your tasks and make sure the **Impostor(s)** don't win!"
        super().__init__(message)


class NotCrewmateError(Exception):
    def __init__(self, ctx, message=None):
        if message is None:
            message = f"You are not a Crewmate! You can't run **{bot.command_prefix(bot, ctx.message)}{ctx.command}**!\n**Tip:** your goal is to kill all the **Crewmates**."
        super().__init__(message)


# On ready handler
@bot.event
async def on_ready():
    lines, chars = 0, 0
    for path in [
        "bot.py",
        "utils.py",
        "cogs/game.py",
        "cogs/owner.py",
        "cogs/management.py",
        "cogs/fun.py",
    ]:
        with open(path) as _file:
            contents = _file.read()
            lines += len(contents.split("\n"))
            chars += len(contents)
    users = bot.get_all_members()
    users = set(users)
    guild, user = "guild", "user"
    print(
        f'\nReady! Connected to {len(bot.guilds)} servers as "{bot.user.name}#{bot.user.discriminator}".\n\nStats:\n{len(users):,} potential users.\n{len(bot_prefixes[guild].values()):,} custom guild prefixes set.\n{len(bot_prefixes[user].values()):,} custom user prefixes set.\nRunning {lines:,} lines of code.\nThere are {chars:,} characters in the bot\'s source code.'
    )
    await bot.change_presence(
        activity=discord.Game(f"Among Us with {len(users):,} people"),
        status=discord.Status.idle,
    )


# Managing command errors
@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, (NotImpostorError, NotCrewmateError)):
        await ctx.message.author.send(exception)
    if isinstance(exception, (commands.CheckFailure, commands.CheckAnyFailure)):
        await ctx.send(exception)
    else:
        await ctx.send(f"```\n{exception}\n```")
        print(exception)


# Automatically delete user messages after 5 seconds
@bot.event
async def on_command(ctx):
    await asyncio.sleep(2.5)
    await ctx.message.delete()


# Load cogs
for cog in ["game", "owner", "fun", "management", "misc"]:
    bot.load_extension(f"cogs.{cog}")


@bot.command(name="reload", aliases=["r"], hidden=True, cog=bot.get_cog("Owner"))
@is_bot_owner()
async def reload(ctx, ext: str):
    bot.reload_extension(ext)


# Run the bot
bot.run("TOKEN")
