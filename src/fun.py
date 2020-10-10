"""
    Among Us Discord Bot - Fun cog file.
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

import discord, secrets
from discord.ext import commands
from checks import is_bot_owner


# Command cog


class Fun(commands.Cog, name="Fun", command_attrs=dict(case_insensitive=True)):
    "Fun commands that are just for messing around with your friends!"

    def __init__(self, bot):
        self.bot = bot
        self.kill_msgs = [
            "**{user}** found out how dynamite works the hard way.",
            "**{user}** got a little *too* friendly with a porcupine.",
            "**{user}** learned just a *little* more about snakes than they wanted to.",
            [
                "**{user}** was abducted by aliens, then kidnapped by the United States government, then abducted by aliens again.",
                "They are *not* having a good day.",
            ],
            "**{user}** got yeeted off a cliff by **{author}**.",
            "**{user}** got rekt lol",
            "Local **{user}** Mauled by One and a Half Bears; Authorities Confused How Half a Bear Can Exist.",
            ["**{user}** thought they could fly.", "They couldn't."],
            ["**{user}** bit the dust.", "It didn't taste very good."],
            "**{user}** was trampled by a flock of wild geese.",
            "**{user}** accidentally dropped the __***BAN HAMMER***__ on their toe.",
            ["**{user}** just kinda fell over.", "What a wimp lol"],
            "**{user}** decided they wanted to eat a knuckle sandwich.",
            "**{user}** was eaten by flying dinosaur laser sharks.",
            "**{author}** blew up because their **Super Mega Death Laser™** (Patent Pending) backfired as they tried to disintegrate **{user}**.",
            [
                "**{user}** self-reported, and get this, it *didn't work*!",
                "*shocked gasp*",
            ],
            [
                "**{user}** used to be alive and well, hanging out with their friends, laughing with them...",
                "But all that changed when the Fire Nation attacked.",
            ],
        ]

    @commands.command(name="echo", aliases=["e"])
    @commands.guild_only()
    async def echo(self, ctx, *, message: str):
        "Make the bot say something!"
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="kill", aliases=["k"])
    async def fun_kill(self, ctx, user: discord.Member):
        """Kill a user (but in a fun way!)
        NOT for the game! Use "a!game kill" for that!"""
        death = secrets.choice(self.kill_msgs)
        if isinstance(death, list):
            for msg in death:
                message = await ctx.send(
                    msg.format(user=user.display_name, author=ctx.author.display_name)
                )
                await asyncio.sleep((message.content.count(" ") + 1) / (10 / 3) + 1.2)
        else:
            await ctx.send(death.format(user=user.display_name, author=ctx.author.display_name))

    @commands.command(name="devkill", aliases=["dk"], hidden=True)
    @is_bot_owner()
    async def dev_kill(self, ctx, user: discord.Member, index: int = None):
        if index is not None:
            death = self.kill_msgs[index]
        else:
            death = secrets.choice(self.kill_msgs)
        if isinstance(death, list):
            for msg in death:
                message = await ctx.send(
                    msg.format(user=user.display_name, author=ctx.author.display_name)
                )
                await asyncio.sleep((message.content.count(" ") + 1) / (10 / 3) + 1.2)
        else:
            await ctx.send(death.format(user=user.display_name, author=ctx.author.display_name))

    @commands.command(name="toad", aliases=["bodhi"])
    @commands.guild_only()
    async def toad(self, ctx):
        'Tell the truth about "Toadman#6234" (aka. Bodhi).'
        await ctx.send(
            "<@!347465489657888769> is soft...\nBut he's this kind of nice, warm loaf of bread soft, not moldy old fruit soft."
        )

    @commands.command(
        name="brandstiftung",
        aliases=["brands", "brand", "stealyohusbando", "husbando"],
    )
    @commands.guild_only()
    async def brandstiftung(self, ctx):
        'Tell the truth about "Mr. Steal Yo Husbando#0460" (aka. Dr. Brandstiftung).'
        await ctx.send(
            "<@!469637323202756608> is not soft, and Bodhi used to think he could be trusted...\nBut then he showed his true colors by murdering an innocent man in cold blood. His relationship with Bodhi may never recover."
        )


def setup(bot):
    bot.add_cog(Fun(bot))
