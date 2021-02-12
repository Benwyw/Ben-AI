import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

description = '''Ben's Python Discord Bot
Using prior experience in developing Ben Kaneki in Java.'''

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', description = description, intents = intents)
bot.remove_command('help')

@bot.event
async def on_ready():   
    # Setting `Listening ` status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help"))
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    channel = bot.get_channel(809741175321264149)
    if message.guild is None and message.author != bot.user:
        #await channel.send("{}: {}".format(message.author,message.content))
        await bot.get_user(254517813417476097).send("{}: {}".format(message.author,message.content))
    await bot.process_commands(message)
'''
    if message.author == bot.user:
        return

    if message.content.startswith('$guild'):
        await message.channel.send(message.guild.id)

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')'''

@bot.command(pass_context=True)
@commands.is_owner()  # The account that owns the bot
async def dm(ctx, target, content):
    target = target.lower()

    if 'ben' in target:
        memberID = 254517813417476097
    elif 'ronald' in target:
        memberID = 525298794653548751
    elif 'chris' in target:
        memberID = 562972196880777226
    elif 'anson' in target:
        memberID = 199877205071888384
    elif 'andy' in target:
        memberID = 407481608560574464

    person = bot.get_user(memberID)

    await ctx.send("Sent a message to: "+str(person))
    await person.send(content)
    await ctx.message.delete()

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        color = discord.Color.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='$add', value='加數', inline=False)

    await author.send(author, embed=embed)
    #await author.send('hi')

load_dotenv()
bot.run(os.getenv('TOKEN'))