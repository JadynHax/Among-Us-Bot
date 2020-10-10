"""
    Among Us Discord Bot - Management cog file.
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

import discord, shutil
from discord.ext import commands
from utils import dump_yaml


class Management(commands.Cog, name="Management", command_attrs=dict(case_insensitive=True)):
    "Bot managing commands (prefix changes, etc.)."

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", aliases=["pre", "p"])
    async def prefix(self, ctx):
        """Various prefix commands!
        If run without a subcommand, sends the prefixes you can use here."""
        if ctx.invoked_subcommand is None:
            guild = ctx.message.guild
            prefix_results = []
            if guild:
                if guild.id in self.bot.bot_prefixes["guild"].keys():
                    prefix_results.append(self.bot.bot_prefixes["guild"][guild.id])

                else:
                    prefix_results.append(self.bot.bot_prefixes["global"])

            else:
                prefix_results.append(self.bot.bot_prefixes["global"])

            if ctx.message.author.id in self.bot.bot_prefixes["user"].keys():
                prefix_results.append(self.bot.bot_prefixes["user"][ctx.message.author.id])

            await ctx.send(
                "You can use the following prefixes here: **"
                + "**, **".join(prefix_results)
                + "**."
            )

    @prefix.command(name="server", aliases=["s"])
    @commands.guild_only()
    async def guild_prefix(self, ctx, prefix=None):
        """Sets the prefix for the server!
        (Setting the server prefix requires the "Manage Server" permission.)
        This overrides the global prefix (a!) and will be permanent through any crashes/downtime.

        Setting the prefix to "none" (or any capitalization thereof) instead removes the prefix. If run without a prefix, it instead sends the current server prefix (does not require "Manage Server")."""
        if prefix is None:
            if ctx.guild.id in self.bot.bot_prefixes["guild"].keys():
                await ctx.send(
                    "**{}** is my custom prefix for **{}**.".format(
                        self.bot.bot_prefixes["guild"][ctx.guild.id], ctx.guild.name
                    )
                )
            else:
                await ctx.send(f"**{ctx.guild.name}** does not have a custom prefix yet.")
        else:
            perms = ctx.message.channel.permissions_for(ctx.message.author)
            if perms.manage_guild:
                self._guild_prefix(ctx.guild.id, prefix)
                await ctx.send(
                    "Done! Your server's custom prefix {}.".format(
                        f"is now {prefix}" if prefix.lower() != "none" else "has been unset"
                    )
                )
            else:
                raise commands.MissingPermissions(["manage_guild"])

    def _guild_prefix(self, _id, prefix):
        if prefix.lower() == "none":
            self.bot.bot_prefixes["guild"].pop(_id)

        else:
            self.bot.bot_prefixes["guild"][_id] = prefix

        dump_yaml(self.bot.bot_prefixes, "prefixes.yml")

        shutil.copy2("prefixes.yml", "drive/My Drive/bot_files/among_us_bot/prefixes.yml")

    @prefix.command(name="user", aliases=["u"])
    async def user_prefix(self, ctx, prefix=None):
        """Sets your custom user prefix!
        Your custom prefix will persist across servers and will be permanent through any crashes/downtime.
        This does not override the global prefix (a!) or any server prefixes. Instead, this is just a prefix you can use in addition to the global/server prefix.

        Setting the prefix to "none" (or any capitalization thereof) instead removes the prefix. If run without a prefix, it instead sends your current custom prefix."""
        if prefix is None:
            if ctx.message.author.id in self.bot.bot_prefixes["user"].keys():
                await ctx.send(
                    "**{}** is your custom prefix.".format(
                        self.bot.bot_prefixes["user"][ctx.message.author.id]
                    )
                )
            else:
                await ctx.send("You don't have a custom prefix... yet!")
        else:
            if prefix.lower() == "none":
                self.bot.bot_prefixes["user"].pop(ctx.message.author.id)
            else:
                self.bot.bot_prefixes["user"][ctx.message.author.id] = prefix

            dump_yaml(self.bot.bot_prefixes, "prefixes.yml")

            shutil.copy2(
                "prefixes.yml",
                "drive/My Drive/bot_files/among_us_bot/prefixes.yml",
            )

            await ctx.send(
                "Done! Your custom prefix {}.".format(
                    f"is now {prefix}" if prefix.lower() != "none" else "has been unset"
                )
            )

    @commands.command(name="ignchans", aliases=["ignorechannels", "ignore", "ic"], hidden=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def ignore_channels(self, ctx, channel: discord.TextChannel):
        pass


def setup(bot):
    bot.add_cog(Management(bot))
