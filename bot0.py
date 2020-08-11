import sqlite3
from json import loads
from os import getenv
from math import ceil

import discord
from discord.utils import get as get_emoji
from dotenv import load_dotenv
from requests import get

import bsmath

load_dotenv()
BRAWL_TOKEN = getenv('BRAWL_TOKEN')

CONN = None

# GAME CONSTANTS
BRAWLER_ORDER = [
    ('SHELLY', 'TROPHY ROAD'), ('NITA', 'TROPHY ROAD'),
    ('COLT', 'TROPHY ROAD'), ('BULL', 'TROPHY ROAD'),
    ('JESSIE', 'TROPHY ROAD'), ('BROCK', 'TROPHY ROAD'),
    ('DYNAMIKE', 'TROPHY ROAD'), ('BO', 'TROPHY ROAD'),
    ('TICK', 'TROPHY ROAD'), ('8-BIT', 'TROPHY ROAD'),
    ('EMZ', 'TROPHY ROAD'), ('EL PRIMO', 'RARE'),
    ('BARLEY', 'RARE'), ('POCO', 'RARE'), ('ROSA', 'RARE'),
    ('RICO', 'SUPER RARE'), ('DARRYL', 'SUPER RARE'), ('PENNY', 'SUPER RARE'),
    ('CARL', 'SUPER RARE'), ('JACKY', 'SUPER RARE'), ('PIPER', 'EPIC'),
    ('PAM', 'EPIC'), ('FRANK', 'EPIC'), ('BIBI', 'EPIC'),
    ('BEA', 'EPIC'), ('NANI', 'EPIC'), ('MORTIS', 'MYTHIC'),
    ('TARA', 'MYTHIC'), ('GENE', 'MYTHIC'), ('MAX', 'MYTHIC'),
    ('MR. P', 'MYTHIC'), ('SPROUT', 'MYTHIC'), ('SPIKE', 'LEGENDARY'),
    ('CROW', 'LEGENDARY'), ('LEON', 'LEGENDARY'), ('SANDY', 'LEGENDARY'),
    ('GALE', 'CHROMATIC'), ('SURGE', 'CHROMATIC')
] # Should ping me if brawler is not in this list

""" API CALLS """
def apirequest(apitail):
    """
    Pulls the API request from the server.
    apitail must be a valid url tail.
    """
    # Open API token, create header
    headers = {
        'Accept': 'application/json',
        'authorization': f'Bearer {BRAWL_TOKEN}'
    }
    # Query server
    response = get(f'https://api.brawlstars.com/v1/{apitail}', headers=headers)
    if response.status_code == 200:
        return loads(response.content.decode('utf-8'))
    HTTPS_RESPONSES = {
        400: "Client provided incorrect parameters for the request.",
        403: "Access denied.",
        404: "Resource not found.",
        429: "Request was throttled.",
        500: "Unknown error.",
        503: "Service is unavailable due to maintenance."
    }
    print(f"Error code: {response.status_code}")
    if response.status_code in HTTPS_RESPONSES:
        print(HTTPS_RESPONSES[response.status_code])
    return None

def get_playerdata(brawltag):
    return apirequest(f"players/%23{brawltag}")

def get_battlelog(brawltag):
    return apirequest(f"players/%23{brawltag}/battlelog")

def get_all_brawlers():
    return apirequest(f"brawlers")['items']

""" DATABASE FUNCTIONS """
def create_connection():
    global CONN
    if CONN is None:
        CONN = sqlite3.connect('brawldata.db')
        CONN.row_factory = sqlite3.Row

def close_connection():
    if CONN is not None:
        CONN.commit()
        CONN.close()

def create_db():
    create_connection()
    sql_create_playerdata = (
        "CREATE TABLE IF NOT EXISTS playerdata("
        "rowid INTEGER PRIMARY KEY,"
        "userid TEXT NOT NULL,"
        "brawltag TEXT NOT NULL,"
        "trackPP INTEGER NOT NULL,"  # Manual entry
        "brawlpass INTEGER,"  # Manual entry
        "tier INTEGER NOT NULL"  # Manual entry
        ")"
    )
    sql_create_progress = (
        "CREATE TABLE IF NOT EXISTS progress("
        "rowid INTEGER PRIMARY KEY,"
        "brawltag TEXT NOT NULL,"
        "brawler TEXT NOT NULL,"
        "points INTEGER NOT NULL"  # Manual entry
        ")"
    )
    sql_create_pphistory = (
        "CREATE TABLE IF NOT EXISTS pphistory("
        "rowid INTEGER PRIMARY KEY,"
        "brawltag TEXT NOT NULL,"
        "date TEXT NOT NULL,"
        "mode TEXT NOT NULL,"
        "map TEXT NOT NULL,"
        "gamenum INTEGER NOT NULL,"
        "brawler TEXT NOT NULL,"
        "trophychange INTEGER NOT NULL"
        ")"
    )
    sql_create_trophyhistory = (
        "CREATE TABLE IF NOT EXISTS trophyhistory("
        "rowid INTEGER PRIMARY KEY,"
        "brawltag TEXT NOT NULL,"
        "date TEXT NOT NULL,"
        "brawler TEXT NOT NULL,"
        "trophy INTEGER NOT NULL"
        ")"
    )
    # CONN.execute(sql_create_playerdata)
    # CONN.execute(sql_create_progress)
    # CONN.execute(sql_create_pphistory)
    # CONN.execute(sql_create_trophyhistory)
    CONN.commit()

def get_brawltag(playerid):
    create_connection()
    sql_get_tag = (
        "SELECT brawltag FROM playerdata WHERE userid = ?"
    )
    tag = CONN.execute(sql_get_tag, (playerid,)).fetchone()
    if tag:
        return tag[0]
    else:
        return None

""" UTILITY FUNCTIONS """
def id(user):
    return '#'.join([str(user.name), str(user.discriminator)])

""" BRAWL FUNCTIONS """
async def update_tag(ctx, args):
    player = ctx.message.author
    playerid = id(player)
    new_brawltag = args[0].upper().replace('#', '')
    playerdata = get_playerdata(new_brawltag)
    # 1. Check if valid playertag
    if playerdata is None:
        await ctx.send("Error, please try again")
        return
    # 2. Check if playertag already in db
    brawltag = get_brawltag(playerid)
    if brawltag is not None:
        # 2a. Update tag, if different
        if brawltag != new_brawltag:
            sql_update_tag = (
                "UPDATE playerdata SET brawltag = ? WHERE userid = ?"
            )
            CONN.execute(sql_update_tag, (new_brawltag, playerid))
            CONN.commit()
            await ctx.send(
                f"Updated tag #{new_brawltag} to {player.mention}."
            )
        else:
            await ctx.send(
                f"{player.mention} already linked to #{new_brawltag}."
            )
    else:
        # 2b. Create new tag
        sql_set_tag = (
            "INSERT INTO playerdata(userid,brawltag,trackPP,brawlpass,tier) "
            "VALUES(?,?,?,?,?)"
        )
        CONN.execute(sql_set_tag, (playerid, new_brawltag, 0, 0, 0))
        CONN.commit()
        await ctx.send(
            f"Linked tag #{new_brawltag} to {player.mention}."
        )

async def check_tag(ctx, args):
    player = ctx.message.author
    brawltag = get_brawltag(id(player))
    if brawltag is not None:
        await ctx.send(f"#{brawltag} is linked to {player.mention}.")
    else:
        await ctx.send(f"There is no tag linked to {player.mention}.")

async def request_brawltag(ctx):
    await ctx.send(
        "Please link your brawltag first with"
        "```.link <tag>```"
        "Your brawltag is the letters and numbers under your picture "
        "in your Brawl Stars profile, following the #."
    )

async def check_missing_brawler(ctx, all_brawlers=None):
    if all_brawlers is None:
        all_brawlers = get_all_brawlers()
    if len(all_brawlers) < len(BRAWLER_ORDER):
        missing = [
            b for b in all_brawlers if b not in list(zip(*BRAWLER_ORDER))[0]]
        await ctx.send(f"<@!278589912184258562> Missing {', '.join(missing)}")

def find_brawler(name, blist):
    for b in blist:
        if b['name'] == name:
            return b
    return None

async def display_levels(ctx, args, emojis):
    player = ctx.message.author
    playerid = id(player)
    brawltag = get_brawltag(playerid)
    if brawltag is None:
        request_brawltag(ctx)
        return
    playerdata = get_playerdata(brawltag)
    all_brawlers = get_all_brawlers()
    max_ga = max([len(x['gadgets']) for x in all_brawlers])
    max_ga = max([len(x['starPowers']) for x in all_brawlers])
    await check_missing_brawler(ctx, all_brawlers=all_brawlers)
    # Prepare items to print
    levels = []
    spga = []
    sp_emoji = str(get_emoji(emojis, name='sp'))
    nosp_emoji = str(get_emoji(emojis, name='nosp'))
    ga_emoji = str(get_emoji(emojis, name='ga'))
    noga_emoji = str(get_emoji(emojis, name='noga'))
    missing_ga_emoji = str(get_emoji(emojis, name='qmga'))
    missing_sp_emoji = str(get_emoji(emojis, name='qmsp'))
    # Loop through all brawlers
    for brawler_name, _ in BRAWLER_ORDER:
        b = find_brawler(brawler_name, playerdata['brawlers'])
        if b is not None:
            # Add to values
            levels.append(str(b['power']))
            max_b = find_brawler(brawler_name, all_brawlers)
            if max_b is None:
                continue
            icons = []
            for ga in max_b['gadgets']:
                if ga in b['gadgets']:
                    icons.append(ga_emoji)
                else:
                    icons.append(noga_emoji)
            for _ in range(max_ga - len(max_b['gadgets'])):
                icons.append(missing_ga_emoji)
            for sp in max_b['starPowers']:
                if sp in b['starPowers']:
                    icons.append(sp_emoji)
                else:
                    icons.append(nosp_emoji)
            for _ in range(max_ga - len(max_b['starPowers'])):
                icons.append(missing_sp_emoji)
            spga.append(' '.join(icons))
        else:
            levels.append('0')
            spga.append('')
    B_PER_PAGE = 24
    totalpages = ceil(len(BRAWLER_ORDER)/B_PER_PAGE)
    for p in range(totalpages):
        embed = discord.Embed(
            colour=0xf0b420
        )
        embed.set_footer(text=f"Page {p+1} of {totalpages}")
        embed.set_author(
            name=player.name,
            icon_url=player.avatar_url
        )
        for index in range(
                B_PER_PAGE*p,
                min(B_PER_PAGE*(p+1), len(BRAWLER_ORDER))):
            if levels[index] != '0':
                value = f"Power {levels[index]}\n"
                value += ''.join(spga[index])
                value += '\u0009\u200b\n\u200b'
            else:
                value = "Locked\n🔒\n\u200b"
            embed.add_field(
                name=BRAWLER_ORDER[index][0],
                value=value,
                inline=True
            )
        if p+1 == totalpages:
            if totalpages % 3 > 0:
                for _ in range(3 - totalpages % 3):
                    embed.add_field(
                        name='\u200b', value='\u200b', inline=True
                    )
        await ctx.send(embed=embed)

async def progression_remaining(ctx, args, emojis):
    player = ctx.message.author
    playerid = id(player)
    brawltag = get_brawltag(playerid)
    if brawltag is None:
        request_brawltag(ctx)
        return
    playerdata = get_playerdata(brawltag)
    all_brawlers = get_all_brawlers()
    await check_missing_brawler(ctx, all_brawlers=all_brawlers)
    brawlers_missing = [
        b['name'] for b in all_brawlers
        if find_brawler(b['name'], playerdata['brawlers']) is None
    ]
    points_remaining = 0
    coins_remaining = 0
    sp_remaining = [0, 0]
    ga_remaining = [0, 0]
    for brawler in playerdata['brawlers']:
        # Points and Coins
        points, coins = bsmath.prog_remaining(brawler['power'])
        #   Check to see if power points are stored
        points_stored = bsmath.points_to_display(0, brawler['power'])[0]
        points_remaining += (points - points_stored)
        coins_remaining += coins
        # SP and Gadgets
        max_brawler = find_brawler(brawler['name'], all_brawlers)
        if max_brawler is None:
            continue
        ga_diff = len(max_brawler['gadgets']) - len(brawler['gadgets'])
        sp_diff = len(max_brawler['starPowers']) - len(brawler['starPowers'])
        if ga_diff > 0:
            ga_remaining[0] += ga_diff
            ga_remaining[1] += 1
        if sp_diff > 0:
            sp_remaining[0] += sp_diff
            sp_remaining[1] += 1
    # Prepare output
    points_emoji = str(get_emoji(emojis, name='powerpoints'))
    coins_emoji = str(get_emoji(emojis, name='coin'))
    ga_emoji = str(get_emoji(emojis, name='ga'))
    sp_emoji = str(get_emoji(emojis, name='sp'))
    gale_emoji = str(get_emoji(emojis, name='Gale_PinGG'))
    embed = discord.Embed(
        colour=0xff03cc
    )
    embed.set_author(
        name=player.name,
        icon_url=player.avatar_url
    )
    embed.description = "Progress to max"
    if len(brawlers_missing) > 0:
        embed.add_field(
            name='Brawlers missing',
            value=', '.join(brawlers_missing),
            inline=False
        )
    if points_remaining > 0 or coins_remaining > 0:
        embed.add_field(
            name='Points and Coins',
            value=(
                f'{points_emoji} {points_remaining} and '
                f'{coins_emoji} {coins_remaining}'
            ),
            inline=False
        )
    if ga_remaining[0] > 0:
        embed.add_field(
            name='Gadgets',
            value=(
                f'{ga_emoji} {ga_remaining[0]} over '
                f'{ga_remaining[1]} brawlers'
            ),
            inline=False
        )
    if sp_remaining[0] > 0:
        embed.add_field(
            name='Star Powers',
            value=(
                f'{sp_emoji} {sp_remaining[0]} over '
                f'{sp_remaining[1]} brawlers'
            ),
            inline=False
        )
    if len(embed.fields) == 0:
        embed.description = f'Your account is maxed! {gale_emoji}'
    await ctx.send(embed=embed)

async def level_distribution(ctx, args):
    player = ctx.message.author
    playerid = id(player)
    brawltag = get_brawltag(playerid)
    if brawltag is None:
        request_brawltag(ctx)
        return
    playerdata = get_playerdata(brawltag)
    all_brawlers = get_all_brawlers()
    await check_missing_brawler(ctx, all_brawlers=all_brawlers)
    leveldist = []
    for b in all_brawlers:
        brawler = find_brawler(b['name'], playerdata['brawlers'])
        if brawler is None:
            leveldist.append('0')
        elif brawler['power'] < 10:
            leveldist.append(str(brawler['power']))
        elif len(brawler['starPowers']) == len(b['starPowers']) \
                and len(brawler['gadgets']) == len(b['gadgets']):
            leveldist.append(';') # 11
        else:
            leveldist.append(':') # 10
    leveldist.sort()
    leveldist = ''.join(sorted(leveldist)).replace(':', '*').replace(';', '!')
    embed = discord.Embed(
        colour=0xf0b420
    )
    embed.set_author(
        name=player.name,
        icon_url=player.avatar_url
    )
    embed.description = (
        'Shows the distribution of brawler power levels at a glance.\n'
        '* denotes power 10s missing at least one gadget or star power.\n'
        '! denotes power 10s with all (released) gadgets and star powers.'
    )
    embed.add_field(
        name='Level Distribution',
        value=f'```[{leveldist}]```'
    )
    await ctx.send(embed=embed)
