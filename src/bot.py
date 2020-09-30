#     Among Us Discord Bot - Main bot file.
#     Copyright (C) 2020  Jason Rutz
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import discord, secrets, json, os, shutil
from discord.ext import commands

# Custom command checks
def is_bot_owner():
  def predicate(ctx):
    if ctx.message.author.id == 710209345832353852:
      return True
    else:
      ctx.send(f'You aren\'t allowed to use this command, {ctx.author.mention}! This is only for the bot owner!')
      return False
  return commands.check(predicate)

# def is_impostor():
#   def predicate(ctx):
#     global players
#     if not ctx.message.author.id in players['impostors']:
#       raise NotImpostorError(ctx)
#   return commands.check(predicate)

# def is_crewmate():
#   def predicate(ctx):
#     global players
#     if not ctx.message.author.id in players['crewmates']:
#       raise NotCrewmateError(ctx)
#   return commands.check(predicate)

# Command cogs
class Owner(commands.Cog, name='Owner', command_attrs=dict(hidden=True)):
  '''
  Owner-only commands.
  '''
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name='prefresh', aliases=['pr'])
  @is_bot_owner()
  async def prefresh(self, ctx):
    global bot_prefixes
    with open('/content/prefixes.json') as prefix_file:
      bot_prefixes = json.load(prefix_file)
    
    await ctx.send('Done refreshing prefixes!')

  @commands.command(name='shutdown', aliases=['fuckoff', 'begone', 'gtfo', 'bye', 'killbot'])
  @is_bot_owner()
  async def shutdown(self, ctx):
    print('Shutdown command run!')
    await ctx.send('Disconnecting...')
    await bot.change_presence(status=discord.Status.offline)
    await bot.close()
    os.kill(os.getpid(), 9)

class Game(commands.Cog, name='Game'):
  '''
  Commands for the Among Us-like Discord game!
  '''
  def __init__(self, bot):
    self.bot = bot

    with open('tasks.json') as taskfile:
      self.tasks = json.load(taskfile)

    print('\nTasks')
    for _map, map_vals in self.tasks.items():
      print(_map)
      for category, _task_list in map_vals.items():
        print('  '+category)
        for _task in _task_list.keys():
          print('    '+_task)
  
  @commands.group(name='task', aliases=['tasks', 't'])
  # Insert "is in game" check? Or should be internal?
  async def task(self, ctx):
    '''
    Task-related commands.
    '''
    if ctx.invoked_subcommand is None:
      await ctx.invoke(help, 'task')
  
  @task.command(name='list', aliases=['l'])
  async def task_list(self, ctx):
    '''
    Lists all tasks from all maps.
    '''
    result = '**List of all tasks:**\n```'
    for _map, map_vals in self.tasks.items():
      result += f'\n{_map}'
      
      for category, _task_list in map_vals.items():
        result += f'\n  {category}'
        for _task in _task_list.keys():
          result += f'\n    {_task}'
    
    result += '\n```'
    await ctx.send(result)

class Management(commands.Cog, name='Management'):
  '''
  Bot managing commands (prefix changes, etc.).
  '''
  def __init__(self, bot):
    self.bot = bot
  
  @commands.group(name='prefix', aliases=['pre', 'p'])
  async def prefix(self, ctx):
    '''
    Various prefix commands!
    If run without a subcommand, sends the prefixes you can use here.
    '''
    if ctx.invoked_subcommand is None:
      guild = ctx.message.guild
      prefix_results = []
      if guild:
        if str(guild.id) in bot_prefixes['guild'].keys():
          prefix_results.append(bot_prefixes['guild'][str(guild.id)])
        
        else:
          prefix_results.append(bot_prefixes['global'])
        
      else:
        prefix_results.append(bot_prefixes['global'])

      if str(ctx.message.author.id) in bot_prefixes['user'].keys():
        prefix_results.append(bot_prefixes['user'][str(ctx.message.author.id)])
      
      await ctx.send('You can use the following prefixes here: `' + '`, `'.join(prefix_results) + '`.')

  @prefix.command(name='server', aliases=['s'])
  @commands.guild_only()
  async def guild_prefix(self, ctx, prefix=None):
    '''
    Sets the prefix for the server!
    (Setting the server prefix requires the "Manage Server" permission.)
    This overrides the global prefix (a!) and will be permanent through any crashes/downtime.

    Setting the prefix to "none" (or any capitalization thereof) instead removes the prefix. If run without a prefix, it instead sends the current server prefix (does not require "Manage Server").
    '''
    if prefix is None:
      if str(ctx.guild.id) in bot_prefixes['guild'].keys():
        await ctx.send('`{}` is my custom prefix for **{}**.'.format(bot_prefixes['guild'][str(ctx.guild.id)], ctx.guild.name))
      else:
        await ctx.send(f'**{ctx.guild.name}** does not have a custom prefix yet.')
    else:
      perms = ctx.message.channel.permissions_for(ctx.message.author)
      if perms.manage_guild:
        self._guild_prefix(ctx.guild.id, prefix)
        await ctx.send('Done! Your server\'s custom prefix {}.'.format(f'is now {prefix}' if prefix.lower() != 'none' else 'has been unset'))
      else:
        raise commands.MissingPermissions(['manage_guild'])

  def _guild_prefix(self, _id, prefix):
    global bot_prefixes
    if prefix.lower() == 'none':
      bot_prefixes['guild'].pop(str(_id), '')

    else:
      bot_prefixes['guild'][str(_id)] = prefix

    with open('prefixes.json', 'w') as prefix_file:
      json.dump(bot_prefixes, prefix_file)

  @prefix.command(name='user', aliases=['u'])
  async def user_prefix(self, ctx, prefix=None):
    '''
    Sets your custom user prefix!
    Your custom prefix will persist across servers and will be permanent through any crashes/downtime.
    This does not override the global prefix (a!) or any server prefixes. Instead, this is just a prefix you can use in addition to the global/server prefix.

    Setting the prefix to "none" (or any capitalization thereof) instead removes the prefix. If run without a prefix, it instead sends your current custom prefix.
    '''
    global bot_prefixes
    if prefix is None:
      if str(ctx.message.author.id) in bot_prefixes['user'].keys():
        await ctx.send('`{}` is your custom prefix.'.format(bot_prefixes['user'][str(ctx.message.author.id)]))
      else:
        await ctx.send('You don\'t have a custom prefix... yet!')
    else:
      if prefix.lower() == 'none':
        bot_prefixes['user'].pop(str(ctx.message.author.id), '')
      else:
        bot_prefixes['user'][str(ctx.message.author.id)] = prefix

      with open('prefixes.json', 'w') as prefix_file:
        json.dump(bot_prefixes, prefix_file)
      
      await ctx.send('Done! Your custom prefix {}.'.format(f'is now {prefix}' if prefix.lower() != 'none' else 'has been unset'))

class Miscellaneous(commands.Cog, name='Miscellaneous'):
  '''
  Miscellaneous commands.
  '''
  def __init__(self, bot):
    self.bot = bot
    help = self.bot.remove_command('help')
    help.cog = self
    self.bot.add_command(help)

  @commands.command(name='invite', aliases=['inv', 'i'])
  async def invite(self, ctx):
    '''
    Sends an invite link for the bot!
    '''
    await ctx.send('Invite me!\nhttps://discord.com/api/oauth2/authorize?client_id=760487866928594974&permissions=268438544&scope=bot')

# Code to run at startup
if not os.path.exists('prefixes.json'):
  with open('prefixes.json', 'w') as prefix_file:
    json.dump({'global': 'a!', 'guild': {}, 'user': {}}, prefix_file)

with open('prefixes.json', 'r') as prefix_file:
  bot_prefixes = json.load(prefix_file)
  print(bot_prefixes)

async def prefix_callable(bot, message):
  guild = message.guild
  prefix_results = []
  if guild:
    if str(guild.id) in bot_prefixes['guild'].keys():
      prefix_results.append(bot_prefixes['guild'][str(guild.id)])
    
    else:
      prefix_results.append(bot_prefixes['global'])
    
  else:
    prefix_results.append(bot_prefixes['global'])

  if str(message.author.id) in bot_prefixes['user'].keys():
    prefix_results.append(bot_prefixes['user'][str(message.author.id)])
  
  return commands.when_mentioned_or(*prefix_results)(bot, message)

bot = commands.Bot(command_prefix=prefix_callable)

# Custom exceptions for error definitions
class NotImpostorError(Exception):
  def __init__(self, ctx, message=None):
    if message is None:
      message = f'You are not an Impostor! You can\'t run `{bot.command_prefix(bot, ctx.message)}{ctx.command}`!\n```Tip: your goal is to kill all the Crewmates.```'
    super().__init__(message)

class NotCrewmateError(Exception):
  def __init__(self, ctx, message=None):
    if message is None:
      message = f'You are not a Crewmate! You can\'t run `{bot.command_prefix(bot, ctx.message)}{ctx.command}`!\n```Tip: your goal is to complete all your tasks and make sure the Impostor(s) don\'t win!```'
    super().__init__(message)

# Managing command errors
@bot.event
async def on_command_error(ctx, exception):
  if isinstance(exception, (NotImpostorError, NotCrewmateError)):
    await ctx.message.author.send(exception)
  else:
    await ctx.send(f'```\n{exception}\n```')
    print(exception)

bot.add_cog(Owner(bot))
bot.add_cog(Game(bot))
bot.add_cog(Management(bot))
bot.add_cog(Miscellaneous(bot))

bot.run("Lmao you don't get the token that easy xD")
