# ---------- PREPARE DISCORD BOT ---------- #

# Load modules and ENV Variables:
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import sqlite3
import math
import random
import pathlib

path = pathlib.PurePath()
intents = discord.Intents.default()
intents.members = True
load_dotenv()


def prefixgetter(bot, message):
    sid = message.guild.id
    prefixes = sqlite3.connect(path / 'data.db')
    cur = prefixes.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS prefixes
                   (serverid INTEGER, prefix TEXT)''')
    cur.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {sid}''')
    default_prefix = "-"
    custom_prefix = cur.fetchone()
    prefixes.close()
    if custom_prefix:
        return str(custom_prefix[0])
    else:
        return default_prefix


# Declare bot prefix:
bot = commands.Bot(command_prefix=prefixgetter, description='A basic bot by Eggo-Plant', intents=intents,
                   case_insensitive=True)


# Add coloring to logs:
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'


# ----------- ERROR HANDLING ---------- #

@bot.event # Sends a message notifying the user if a command is on cooldown.
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))


# ----------- INITIALIZE BOT ---------- #

# Commands to be run on boot:
@bot.event
async def on_ready():
    # Booting info:
    print(
        bcolors.OKCYAN + "[INFO]: " + bcolors.ENDC + bcolors.OKGREEN + bcolors.BOLD + "Successful Login! " + bcolors.ENDC)
    print(
        bcolors.OKCYAN + "[INFO]: " + bcolors.ENDC + "Logged in as: " + bcolors.OKCYAN + bcolors.HEADER + bcolors.ITALIC + "{bot_username}".format(
            bot_username=bot.user.name) + bcolors.ENDC)
    print(
        bcolors.OKCYAN + "[INFO]: " + bcolors.ENDC + "Bot ID: " + bcolors.OKCYAN + bcolors.HEADER + bcolors.ITALIC + "{bot_user_id}".format(
            bot_user_id=bot.user.id) + bcolors.ENDC)

    # Set bot's status
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name="Ping me for my prefix!"))
    print(bcolors.OKCYAN + "[INFO]: " + bcolors.ENDC + bcolors.OKGREEN + "Bot status set! " + bcolors.ENDC)
    print('----------------------------------------------------------------------')  # Just a hyphen seperator


@bot.event
async def on_message(ctx):
    if "<@!828620863632048199>" in ctx.content:
        await ctx.channel.send(f'`{prefixgetter(1, ctx)}` is my prefix!')
    if "<@828620863632048199>" in ctx.content:
        await ctx.channel.send(f'`{prefixgetter(1, ctx)}` is my prefix!')

    await bot.process_commands(ctx)


# ---------- DEFINING FUNCTIONS ---------- #

# Coinflip function
async def flip_a_coin():
    coin = random.choice(["Heads", "Tails"])
    return coin


# ---------- DISCORD BOT COMMANDS ---------- #

@bot.command(name="ping", aliases=["latency"], help="Displays the bot's message latency.")
@commands.cooldown(3, 5, commands.BucketType.user)
async def ping(message):
    await message.channel.send(f':ping_pong: **Pong!** Response time is: {math.floor(bot.latency * 1000)}ms')


@bot.command(name="quote", aliases=["quotes"], help="Displays a random proverb.")
@commands.cooldown(1, 3)
async def quote(message):
    response = requests.get('https://api.quotable.io/random?tags=wisdom').json()
    quote = (f'''"{response['content']}" -{response['author']}''')
    await message.channel.send(quote)


@bot.command(name="mcsrv", aliases=["mcstatus"], help="Supply a minecraft server address to query")
@commands.cooldown(1, 5)
async def mcsrv(ctx, *, message: str):
    response = requests.get(f'https://api.mcsrvstat.us/2/{message}').json()
    online: bool = response['debug']['ping']
    if online:
        n = '\n' # I have to do this because you can't put \n inside of f strings
        embed=discord.Embed(title="<:fullbars:829457395213140029> Server is Online!", description=f"**Server Address:** {response['ip']}{n} **Server Port:** {response['port']}{n} **Players Online:** {response['players']['online']}{n} **Server Version:** {response['version']}", color=0x00FF21)
        await ctx.channel.send(embed=embed)
    else:
        embed=discord.Embed(title="<:nobars:829458356141424672> Server is Offline!", description="Sorry! Either the server is offline, or the address supplied is incorrect.", color=0xff0000)
        await ctx.channel.send(embed=embed)


@bot.command(name="coinflip", aliases=["cf"], help="Flips a coin.")
@commands.cooldown(1, 2)
async def coinflip(message):
    coin = await flip_a_coin()
    await message.channel.send(f':coin: You got **{coin}**!')


@bot.command(name="mcw", alias=["minecraftwiki"], help="Provide a search term for the Minecraft wiki (e.x. 'mcw iron golem').")
async def mcw(ctx, *, message: str):
    search_term = message.replace(' ', '_')
    adjusted_search = search_term.lower()
    wiki_link = (f"https://minecraft.fandom.com/wiki/{adjusted_search}")
    await ctx.send(wiki_link)


@bot.command(name="tw", alias=["terrariawiki"], help="Provide a search term for the Terraria wiki (e.x. 'tw blood moon').")
async def mcw(ctx, *, message: str):
    search_term = message.replace(' ', '_')
    adjusted_search = search_term.title()
    wiki_link = (f"https://terraria.fandom.com/wiki/{adjusted_search}")
    await ctx.send(wiki_link)


@bot.command(name="prefix", alias=["setprefix"], help="Use this to change my prefix (admins only)")
@commands.has_permissions(administrator=True)
async def prefix(ctx, newprefix):
    serverid = ctx.guild.id
    prefixesls = sqlite3.connect(path / 'data.db')
    cur = prefixesls.cursor()
    cur.execute(f'''SELECT prefix FROM prefixes WHERE serverid = {serverid}''')
    if cur.fetchone() is not None:
        cur.execute("""UPDATE prefixes SET prefix = ? WHERE serverid = ?""", (newprefix, serverid))
    else:
        cur.execute("INSERT INTO prefixes(serverid, prefix) VALUES (?,?)",
                    (serverid, newprefix))
    prefixesls.commit()
    prefixesls.close()
    await ctx.send(f"Prefix set to {newprefix}")


# ---------- IMPORT TOKEN FROM ENV VARIABLE ---------- #

bot.run(os.getenv('TOKEN'))
