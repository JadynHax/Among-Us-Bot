"""
    Among Us Discord Bot - Miscellaneous cog file.
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
from discord.ext import commands


# Command cog


class Miscellaneous(
    commands.Cog,
    name="Miscellaneous",
    command_attrs=dict(case_insensitive=True),
):
    "Miscellaneous commands."

    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command.cog = self

    @commands.command(name="invite", aliases=["inv", "i"])
    async def invite(self, ctx):
        "Sends an invite link for the bot!"
        await ctx.send(
            "Invite me!\nhttps://discord.com/api/oauth2/authorize?client_id=760487866928594974&permissions=268438544&scope=bot"
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
