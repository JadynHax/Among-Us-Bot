"""
    Among Us Discord Bot - Bot command checks.
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
from discord.ext import commands


def is_bot_owner():
    def predicate(ctx):
        if ctx.message.author.id == 710209345832353852:
            return True
        else:
            raise commands.CheckFailure(
                f"You aren't allowed to use this command, {ctx.author.mention}! This is only for the bot owner!"
            )

    return commands.check(predicate)
