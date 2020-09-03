from os import getenv

from discord.ext import commands
from dotenv import load_dotenv

import bot0
import powerplay
import timer
import trophyleague

load_dotenv()
DISCORD_TOKEN = getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='.')
# bot.remove_command('help')

def channel(channelid):
    return bot.get_channel(channelid)

@bot.event
async def on_ready():
    print("Beep boop I'm a bot")
    await timer.minute_timer(channel, bot.emojis)

@bot.command(name='prefix')
async def change_prefix(ctx, *args):
    prefix = args[0][0]
    bot.command_prefix = prefix
    await ctx.send(f"Prefix changed to {prefix}")

@bot.command(name='about')
async def about(ctx):
    await ctx.send(
        "A quick little Discord bot written by <@!278589912184258562>.\n"
        "This content is not affiliated with, endorsed, sponsored, or "
        "specifically approved by Supercell and Supercell is not responsible "
        "for it. For more information see Supercell’s Fan Content Policy: "
        "www.supercell.com/fan-content-policy.")

@bot.command(name='link')
async def update_tag(ctx, *args):
    await bot0.update_tag(ctx, args)

@bot.command(name='test')
async def testing(ctx):
    await ctx.send("Beep boop I'm a bot 🤖")

@bot.command(name='tag')
async def get_tag(ctx, *args):
    await bot0.check_tag(ctx, args)

@bot.command(name='levels', aliases=['l'])
async def display_levels(ctx, *args):
    await trophyleague.display_levels(ctx, args, bot.emojis)

@bot.command(name='progression', aliases=['prog'])
async def progression_remaining(ctx, *args):
    await trophyleague.progression_remaining(ctx, args, bot.emojis)

@bot.command(name='leveldist', aliases=['dist'])
async def level_distribution(ctx, *args):
    await trophyleague.level_distribution(ctx, args)

@bot.command(name='search', aliases=['s'])
async def powerplay_search(ctx, *args):
    await powerplay.pp_search(ctx, args)

@bot.command(name='profile', aliases=['p'])
async def profile(ctx, *args):
    await trophyleague.profile(ctx, args, bot.emojis)

bot.run(DISCORD_TOKEN)
