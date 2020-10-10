"""
    Among Us Discord Bot - Among Us Bot utilities.
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

import yaml, os, shutil


get_guild_pre = (
    lambda bot, guild: bot.bot_prefixes["global"]
    if guild.id not in bot.bot_prefixes["guild"].keys()
    else bot.bot_prefixes["guild"][guild.id]
)


def dump_yaml(obj: dict, path: str) -> None:
    with open(path, "w") as out:
        out.write(yaml.dump(obj, Dumper=yaml.CDumper))

    shutil.copy2(
        path,
        f"/content/drive/My Drive/bot_files/among_us_bot/{os.path.split(path)}",
    )


def load_yaml(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as yamlfile:
            return yaml.load(yamlfile.read(), Loader=yaml.CLoader)
    else:
        print(f"Unable to load {path}! {path} does not exist!")
