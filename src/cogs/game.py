"""
    Among Us Discord Bot - Game cog file.
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

import discord
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks as disc_tasks
from typing import Union
from utils import load_yaml, dump_yaml, get_guild_pre


# Command cog


class Game(commands.Cog, name="Game", command_attrs=dict(case_insensitive=True)):
    "Commands for the Among Us Bot's Discord game!"

    def is_game_running():
        def predicate(ctx):
            games = self.bot.get_cog("Game").games
            if ctx.guild.id not in games.keys():
                raise commands.CheckFailure("There isn't a game running in this server!")
            return True

        return commands.check(predicate)

    def __init__(self, bot):
        self.games = {}
        self.game_setup = {}
        self.tasks = {}
        self.maps = {}
        self.bot = bot
        self.tasks = load_yaml("tasks.yml")
        self.game_setup = load_yaml("game-setup.yml")
        self.maps = load_yaml("maps.yml")

        print("\nTasks")
        for _map, map_vals in self.tasks.items():
            print("  " + _map)
            for category, _task_list in map_vals.items():
                print("    " + category)
                for _task in _task_list.keys():
                    print("      " + _task)

        self.close_inactive_lobbies.start()

    @disc_tasks.loop(seconds=10)
    async def close_inactive_lobbies(self):
        keys = [
            k
            for k in self.games.keys()
            if +(datetime.today() - self.games[k]["active_at"]) > timedelta(minutes=20)
        ]

        for k in keys:
            await self.games[k]["lobby_message"].edit(
                content="Closed due to inactivity! Try to start the game if people are no longer actively joining, otherwise we have to close the lobby to save on RAM."
            )
            await self.games[k]["full_context"].send(
                "Sorry! We had to close your lobby due to inactivity."
            )
            del self.games[k]

    @commands.group(name="game", aliases=["g"])
    @commands.guild_only()
    async def game(self, ctx):
        "Game configuration and startup commands."
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand!")
            await ctx.send_help(ctx.command)

    @game.command(name="prep", aliases=["prepare", "p"])
    @commands.guild_only()
    async def game_prepare(self, ctx):
        "Prepare a game lobby that others in the server can join!"
        if not ctx.guild.id in self.games.keys():
            guild = ctx.message.guild
            prefix = get_guild_pre(self.bot, guild)
            message = await ctx.send(
                f"**{ctx.author.display_name}** is hosting an Among Us Bot lobby! Type the command **{prefix}game join** to join!\nThere is currently **1** player in the lobby."
            )
            self.games[ctx.guild.id] = {
                "lobby_message": message,
                "host": ctx.author,
                "active_at": datetime.today(),
                "num_players": 1,
                "num_impostors": 2,
                "walk_cooldown": 5,
                "lights_perm_edit": False,
                "tasks": {"long": 1, "short": 2, "common": 1},
                "player_ids": [ctx.author.id],
                "full_context": ctx,
                "in_game": False,
                "map": "Mira HQ",
            }

        else:
            message = await ctx.send(
                "Sorry! There's already a lobby running in your server! As of right now, this bot is incapable of handling more than one game per server."
            )
            await asyncio.sleep(10)
            await message.delete()

    @game.command(name="join", aliases=["j"])
    @commands.guild_only()
    @is_game_running()
    async def game_join(self, ctx):
        """Join a game lobby!
        Only works if there's a lobby running on the server."""
        _game = self.games[ctx.guild.id]

        if ctx.author.id not in _game["player_ids"]:
            _game["player_ids"].append(ctx.author.id)
            _game["active_at"] = datetime.today()
            _game["num_players"] += 1
            guild = ctx.message.guild
            prefix = get_guild_pre(self.bot, guild)

            await _game["lobby_message"].edit(
                content="**{0.display_name}** is hosting an Among Us Bot lobby! Type the command **{prefix}game join** to join!\nThere {1} currently **{2}** {3} in the lobby.".format(
                    _game["host"],
                    "is" if _game["num_players"] == 1 else "are",
                    _game["num_players"],
                    "player" if _game["num_players"] == 1 else "players",
                    prefix=prefix,
                )
            )
            message = await ctx.send(
                "Joined successfully! There are now **{}** players in this lobby. See the lobby message for lobby details.".format(
                    _game["num_players"]
                )
            )

            self.games[ctx.guild.id] = _game
            await asyncio.sleep(10)
            await message.delete()

        else:
            message = await ctx.send("You're already in this lobby!")
            await asyncio.sleep(10)
            await message.delete()

    @game.command(name="leave", aliases=["l"])
    @commands.guild_only()
    @is_game_running()
    async def game_leave(self, ctx):
        """Leave a game lobby!
        Only works if there's a lobby running on the server and you're in it."""
        _game = self.games[ctx.guild.id]

        if ctx.author.id in _game["player_ids"]:
            if ctx.author != _game["host"]:
                _game["player_ids"].remove(ctx.author.id)
                _game["num_players"] -= 1
                guild = ctx.message.guild
                prefix = get_guild_pre(self.bot, guild)

                await _game["lobby_message"].edit(
                    content="**{0.author.display_name}** is hosting an Among Us Bot lobby! Type the command **{prefix}game join** to join!\nThere {1} currently **{2}** {3} in the lobby.".format(
                        _game["full_context"],
                        "is" if _game["num_players"] == 1 else "are",
                        _game["num_players"],
                        "player" if _game["num_players"] == 1 else "players",
                        prefix=prefix,
                    )
                )
                message = await ctx.send(
                    "Left successfully! There {0} now **{1}** {2} in this lobby. See the lobby message for lobby details.".format(
                        "is" if _game["num_players"] == 1 else "are",
                        _game["num_players"],
                        "player" if _game["num_players"] == 1 else "players",
                    )
                )

                self.games[ctx.guild.id] = _game
                await asyncio.sleep(10)
                await message.delete()

            else:
                guild = ctx.message.guild
                if guild:
                    if str(guild.id) in self.bot.bot_prefixes["guild"].keys():
                        prefix = self.bot.bot_prefixes["guild"][str(guild.id)]

                    else:
                        prefix = self.bot.bot_prefixes["global"]

                user = _game["host"]
                await _game["lobby_message"].edit(
                    content=f"**{user.display_name}** closed their lobby! Type the command **{prefix}game prep** to make a new one."
                )
                message = await ctx.send("Closed your lobby!")

                self.games.pop(ctx.guild.id)
                await asyncio.sleep(10)
                await message.delete()

        else:
            message = await ctx.send("You're already not in this lobby!")
            await asyncio.sleep(10)
            await message.delete()

    @game.group(name="setup", aliases=["s"])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True, manage_roles=True)
    async def setup(self, ctx):
        'Automatically set up the game, or edit setup options manually. Only if you have the "manage channels" and "manage roles" permissions, though!'
        if ctx.invoked_subcommand is None:
            setup_msg = await ctx.send("Setting up game categories, channels, and roles...")
            category_overwrites = discord.PermissionOverwrite(
                **{k: v for k, v in iter(discord.Permissions.none())}
            )
            in_game_role = await ctx.guild.create_role(name="In-Game", reason="Among Us Bot setup")
            dead_role = await ctx.guild.create_role(name="Dead", reason="Among Us Bot setup")
            game_setup = {
                "in_game_role": in_game_role.id,
                "dead_role": dead_role.id,
            }

            for map_name, game_map in self.maps.items():
                category = await ctx.guild.create_category(
                    map_name,
                    overwrites={role: category_overwrites for role in ctx.guild.roles},
                    reason="Among Us Bot setup",
                )
                meeting_chan = await category.create_text_channel(
                    "meeting-chat", reason="Among Us Bot setup"
                )
                room_chans = {"Meeting": meeting_chan.id}

                for room in game_map.keys():
                    room_chan = await category.create_text_channel(
                        "-".join(room.lower().split(" ")),
                        reason="Among Us Bot setup",
                    )
                    room_chans[room] = room_chan.id

                game_setup[map_name] = {
                    "category": category.id,
                    "channels": room_chans,
                }

            self.game_setup[ctx.guild.id] = game_setup

            dump_yaml(self.game_setup, "game-setup.yml")
            await setup_msg.edit(content="Done setting up!")
            await asyncio.sleep(10)
            await setup_msg.delete()

    @setup.command(name="delete", aliases=["d"])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True, manage_roles=True)
    async def delete(self, ctx):
        "Deletes automatically set up categories, channels, etc."
        if ctx.guild.id in self.game_setup:
            deleting_msg = await ctx.send("Deleting auto-set-up categories, channels, and roles...")
            game_setup = self.game_setup[ctx.guild.id]
            del self.game_setup[ctx.guild.id]

            for game_map in game_setup.values():
                if not isinstance(game_map, int):
                    for id in game_map["channels"].values():
                        if ctx.guild.get_channel(id) is not None:
                            if ctx.guild.get_channel(id).category is not None:
                                await ctx.guild.get_channel(id).category.delete(
                                    reason="Among Us Bot auto-deletion"
                                )
                            await ctx.guild.get_channel(id).delete(
                                reason="Among Us Bot auto-deletion"
                            )

            in_game_role = ctx.guild.get_role(int(game_setup["in_game_role"]))
            if in_game_role is not None:
                await in_game_role.delete(reason="Among Us Bot auto-deletion")

            dead_role = ctx.guild.get_role(int(game_setup["dead_role"]))
            if dead_role is not None:
                await dead_role.delete(reason="Among Us Bot auto-deletion")

            dump_yaml(self.game_setup, "game-setup.yml")
            await deleting_msg.edit(content="Done!")
            await asyncio.sleep(10)
            await deleting_msg.delete()

    @game.command(name="configure", aliases=["config", "c"])
    @commands.guild_only()
    @is_game_running()
    async def configure(
        self,
        ctx,
        option: str = None,
        *args: Union[discord.Member, discord.User, int, str],
    ):
        """Lobby configuration commands.
        Run without specifying a game option to display all of the lobby's current configuration values.
        Run with an option and no argument to display that option's current value.

        Game Options:
            [host|h] <user>: Change the lobby's host to <user>.
            [walk|w] <cooldown>: Set the walk command's cooldown to <cooldown>.
            [impostors|imps|imp|i] <amount>: Set the number of impostors to <amount>.
            [tasks|t] <long|short|common> <amount>: Set the amount of <task_type> tasks to <amount>.
            [sabotageperms|sabperms|sp] <yes/y/true|no/n/false> [specific_perm_1] [specific_perm_2]: Sets the value of [specific_perm]s (or all perm edits, if not specified) to True or False, depending on the other argument."""
        _game = self.games[ctx.guild.id]
        if option is None:
            desc_text = """Host: **{0.name}#{0.discriminator}**
Number of Impostors: **{1}**
Cooldown for walk command: **{2}**
Does sabotaging lights make crewmates unable to see message history? **{3}**
Map: **{4}**""".format(
                _game["host"],
                _game["num_impostors"],
                _game["walk_cooldown"],
                _game["lights_perm_edit"],
                _game["map"],
            )
            tasks = _game["tasks"]
            task_counts = """Long: **{0}**
Short: **{1}**
Common: **{2}**""".format(
                tasks["long"], tasks["short"], tasks["common"]
            )

            embed = discord.Embed(title="Game Options", description=desc_text, color=0x96D0B0)
            embed.add_field(name="Task Counts", value=task_counts, inline=False)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(15)
            await message.delete()

        # Only let host perform game configuration
        elif ctx.author == _game["host"]:
            message = None
            if len(args) > 0:
                self.games[ctx.guild.id]["active_at"] = datetime.today()

            # Host subcommand
            if option.lower() in ["host", "h"]:
                if len(args) > 0:
                    user = args[0]

                    if user == ctx.author:
                        message = await ctx.send("Can't change lobby host to yourself!")

                    elif user.id not in _game["player_ids"]:
                        message = await ctx.send(
                            "Can't change lobby host to a user that's not in this lobby!"
                        )

                    else:
                        prefix = get_guild_pre(self.bot, ctx.guild)
                        _game["host"] = user
                        _game["active_at"] = datetime.today()
                        await _game["lobby_message"].edit(
                            content="**{0.display_name}** is hosting an Among Us Bot lobby! Type the command **{prefix}game join** to join!\nThere {1} currently **{2}** {3} in the lobby.".format(
                                user,
                                "is" if _game["num_players"] == 1 else "are",
                                _game["num_players"],
                                "player" if _game["num_players"] == 1 else "players",
                                prefix=prefix,
                            )
                        )
                        self.games[ctx.guild.id] = _game
                        message = await ctx.send(
                            f"Successfully made **{user.display_name}** the lobby's host!"
                        )

                else:
                    message = await ctx.send(
                        "The current host is **{}**.".format(_game["host"].display_name)
                    )

            # Walk cooldown subcommand
            elif option.lower() in ["walk", "w"]:
                if len(args) > 0:
                    cooldown = args[0]
                    self.games[ctx.guild.id]["walk_cooldown"] = cooldown
                    message = await ctx.send(
                        f"Successfully set the walk command cooldown to **{cooldown}**!"
                    )

                else:
                    message = await ctx.send(
                        "The current walk cooldown is **{}**.".format(_game["walk_cooldown"])
                    )

            # Impostor subcommand
            elif option.lower() in ["impostors", "imps", "imp", "i"]:
                if len(args) > 0:
                    amount = args[0]

                    if 0 < amount < 6:
                        self.games[ctx.guild.id]["num_impostors"] = amount
                        message = await ctx.send(
                            f"Successfully set the number of impostors to **{amount}**!"
                        )

                    else:
                        message = await ctx.send("Please choose a number from 1 to 5!")

                else:
                    message = await ctx.send(
                        "The current number of impostors is **{}**".format(_game["num_impostors"])
                    )

            # Task subcommand
            elif option.lower() in ["tasks", "t"]:
                if len(args) >= 2:
                    task_type, amount = args[0], args[1]

                    if task_type in self.games[ctx.guild.id]["tasks"].keys():
                        if amount > len(self.tasks[self.games[ctx.guild.id]["map"]]):
                            message = await ctx.send(
                                f"Can't set the amount of **{task_type.lower()}** tasks to **{amount}**; not enough **{task_type.lower()}** tasks on the map!"
                            )

                        else:
                            self.games[ctx.guild.id]["tasks"][task_type] = amount
                            message = await ctx.send(
                                f"Successfully set the number of **{task_type.lower()}** tasks to **{amount}**!"
                            )

                    else:
                        message = await ctx.send(
                            f'There\'s no such thing as "**{task_type.lower()}**" tasks!'
                        )

                else:
                    message = await ctx.send(
                        "Invalid number of arguments! You should pass both **task_type** and **amount** to this command!"
                    )

            # Sabatoge permissions subcommand
            elif option.lower() in ["sabotageperms", "sabperms", "sp"]:
                if len(args) >= 2:
                    tf_check, *perms = args
                elif len(args) == 1:
                    tf_check, perms = args[0], None
                else:
                    message = await ctx.send(
                        "Specific permission edits are `lights` and `o2`, at least for now!"
                    )

            else:
                message = await ctx.send(
                    "Invalid subcommand! See the command help for valid subcommands!"
                )

            await asyncio.sleep(10)
            await message.delete()

        else:
            message = await ctx.send("You can't use this command—you aren't the lobby's host!")
            await asyncio.sleep(10)
            await message.delete()

    @game.command(name="listplayers", aliases=["listp", "lp"])
    @commands.guild_only()
    @is_game_running()
    async def list_players(self, ctx):
        "List all players in a lobby!"
        _game = self.games[ctx.guild.id]
        msg = "**Players in lobby:**\n"

        for _id in _game["player_ids"]:
            msg += ctx.guild.get_member(_id).display_name + "\n"

        message = await ctx.send(msg)
        await asyncio.sleep(10)
        await message.delete()

    @commands.group(name="task", aliases=["tasks", "t"])
    async def task(self, ctx):
        "Task-related commands."
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @task.command(name="listall", aliases=["la"])
    async def task_list(self, ctx):
        "Lists all tasks from all maps."
        result = "**List of all tasks:**\n```"
        for _map, map_vals in self.tasks.items():
            result += f"\n{_map}"

            for category, _task_list in map_vals.items():
                result += f"\n  {category}"
                for _task in _task_list.keys():
                    result += f"\n    {_task}"

        result += "\n```"
        await ctx.send(result)


def setup(bot):
    bot.add_cog(Game(bot))
