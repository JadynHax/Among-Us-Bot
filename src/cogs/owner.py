"""
    Among Us Discord Bot - Owner cog file.
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

import discord, os, copy
from typing import Union
from discord.ext import commands
from utils import load_yaml
from checks import is_bot_owner


# Command cog


class Owner(
    commands.Cog,
    name="Owner",
    command_attrs=dict(hidden=True, case_insensitive=True),
):
    "Owner-only commands."

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefresh", aliases=["pr"])
    @is_bot_owner()
    async def prefresh(self, ctx):
        self.bot.bot_prefixes = load_yaml("prefixes.yml")

        await ctx.send("Done refreshing prefixes!")

    @commands.command(name="shutdown", aliases=["fuckoff", "begone", "gtfo", "bye", "killbot"])
    @is_bot_owner()
    async def shutdown(self, ctx):
        print("Shutdown command run!")
        await ctx.send("Disconnecting...")
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.close()
        os.kill(os.getpid(), 9)

    @commands.command(name="runas", aliases=["ra"])
    @is_bot_owner()
    async def run_as(self, ctx, user: commands.MemberConverter, *, command: str):
        run_as_msg = copy.copy(ctx.message)
        run_as_msg._update(dict(channel=ctx.channel, content=f"{ctx.prefix}{command}"))
        run_as_msg.author = user
        run_as_ctx = await self.bot.get_context(run_as_msg)
        await self.bot.invoke(run_as_ctx)

    @commands.command(name="gameinfo", aliases=["ginfo", "gi"])
    @is_bot_owner()
    async def game_info(self, ctx, guild: discord.Guild):
        games = self.bot.get_cog("Game").games
        if guild.id in games.keys():
            result = f"```\nGame lobby in {guild.name}\n"
            for k, v in games[guild.id].items():
                if isinstance(v, discord.Message):
                    result += f"{k}: ID: {v.id}\n\tGuild Name: {v.author.guild.name}\n\tGuild ID: {v.author.guild.id}\n\tType: {v.type}\n\tChannel: {v.channel.name}\n"
                elif isinstance(v, commands.Context):
                    result += f"{k}: Prefix used: {v.prefix}\n\tLobby creator: {v.author.name}#{v.author.discriminator}\n\tCreator's ID:  {v.author.id}\n"
                else:
                    result += f"{k}: {v}\n"
            result += "```"
            await ctx.send(result)

    @commands.command(name="fucktext", aliases=["ft"])
    @is_bot_owner()
    async def fucktext(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send("||" + "||||".join(message) + "||")

    @commands.command(name="proxy")
    @is_bot_owner()
    async def proxy(
        self,
        ctx,
        channel: Union[discord.TextChannel, discord.Member, discord.User],
        *,
        message: str,
    ):
        await channel.send(message)
        await ctx.send(f'Sent "{message}" to **{channel.name}**.')

    @commands.command(name="botalert", aliases=["alert", "ba"])
    @is_bot_owner()
    async def send_bot_alert(self, ctx, *, message: str):
        msg = await ctx.send("Sending bot alert...")
        async with ctx.typing():
            for guild in self.bot.guilds:
                sys_chan = guild.system_channel

                if (
                    sys_chan is not None
                    and sys_chan.permissions_for(guild.get_member(self.bot.user.id)).send_messages
                ):
                    await sys_chan.send(message)

                else:
                    for channel in guild.channels:
                        if channel.permissions_for(
                            guild.get_member(self.bot.user.id)
                        ).send_messages:
                            try:
                                await channel.send(message)
                                break
                            except:
                                pass
                        else:
                            print(f"Sending alert failed in server: {guild.name}")
            await msg.edit(content="Done!")


def setup(bot):
    bot.add_cog(Owner(bot))
