"""
This module contains API calls and database functions.
"""

import sqlite3
from json import load, loads
from os import getenv

from dotenv import load_dotenv
from requests import get

load_dotenv()
BRAWL_TOKEN = getenv('BRAWL_TOKEN')

CONN = None


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
        "date TEXT NOT NULL,"
        "battletime TEXT NOT NULL,"
        "mode TEXT NOT NULL,"
        "map TEXT NOT NULL,"
        "p1tag TEXT NOT NULL,"
        "p1brawler TEXT NOT NULL,"
        "p2tag TEXT,"
        "p2brawler TEXT,"
        "p3tag TEXT,"
        "p3brawler TEXT,"
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
    CONN.execute(sql_create_playerdata)
    CONN.execute(sql_create_progress)
    CONN.execute('DROP TABLE pphistory')
    CONN.execute(sql_create_pphistory)
    CONN.execute(sql_create_trophyhistory)
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

def insert_pp(date, battletime, mode, bmap, trophychange, p1tag, p1brawler,
        p2tag=None, p2brawler=None, p3tag=None, p3brawler=None):
    """
    trophychange is int type, all else is str type
    """
    sql_insert_pp = (
        "INSERT INTO pphistory(date,battletime,mode,map,p1tag,p1brawler,p2tag,"
        "p2brawler,p3tag,p3brawler,trophychange) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?)"
    )
    values = (
        date, battletime, mode, bmap, p1tag, p1brawler, p2tag, p2brawler,
        p3tag, p3brawler, trophychange
    )
    create_connection()
    CONN.execute(sql_insert_pp, values)
    CONN.commit()

# create_db()
# insert_pp(
#     "2020-09-01", "20200902T002017.000Z", "duoShowdown", "Will of the Wisp",
#     34, "UULVQY2L", "CROW", p2tag="8CRJJ2JR9", p2brawler="GENE"
# )
# insert_pp(
#     "2020-09-01", "20200902T002257.000Z", "duoShowdown", "Will of the Wisp",
#     4, "UULVQY2L", "CROW", p2tag="8CRJJ2JR9", p2brawler="GENE"
# )
# insert_pp(
#     "2020-09-01", "20200902T002429.000Z", "duoShowdown", "Will of the Wisp",
#     26, "UULVQY2L", "CROW", p2tag="8CRJJ2JR9", p2brawler="GENE"
# )
# insert_pp(
#     "2020-09-01", "20200902T011901.000Z", "duoShowdown", "Will of the Wisp",
#     2, "22GV9VL", "SURGE", p2tag="QRGRYJGR", p2brawler="CROW"
# )
# insert_pp(
#     "2020-09-01", "20200902T011944.000Z", "duoShowdown", "Will of the Wisp",
#     34, "22GV9VL", "SURGE", p2tag="8J0VRU0C", p2brawler="SPROUT"
# )
# insert_pp(
#     "2020-09-01", "20200902T012209.000Z", "duoShowdown", "Will of the Wisp",
#     10, "22GV9VL", "SURGE", p2tag="P08G0L98", p2brawler="PAM"
# )

def battle_exists(battletime, tag):
    """
    Returns True if the battletime exists and includes the tag.
    """
    sql_select_battle = (
        "SELECT p1tag, p2tag, p3tag FROM pphistory WHERE battletime = ?"
    )
    create_connection()
    rows = CONN.execute(sql_select_battle, (str(battletime),)).fetchall()
    for row in rows:
        if tag in row:
            return True
    return False

""" UTILITY FUNCTIONS """
def id(user):
    return '#'.join([str(user.name), str(user.discriminator)])

def profile_icon(icon_id, default=''):
    with open('icon.json') as f:
        icondict = load(f)
    return icondict.get(icon_id, default)

""" BRAWL FUNCTIONS """
async def update_tag(ctx, args):
    if len(args) == 0:
        await request_brawltag(ctx)
        return
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
