"""
All functions related to Power Play.
"""

from datetime import datetime, timedelta
from json import load
from pprint import pprint

import discord
from discord.utils import get as get_emoji

from bot0 import battle_exists, get_battlelog, insert_pp

PPSQUAD = ['JQU8Y00R', '22GV9VL', 'UULVQY2L']


def battletime(timestr):
    """
    Returns the date of battle as a datetime in the Power Play time zone.
    """
    return (datetime(
        int(timestr[:4]), int(timestr[4:6]), int(timestr[6:8]),
        hour=int(timestr[9:11]), minute=int(timestr[11:13])
    ) - timedelta(hours=2)).date()

async def auto_pp_search(channel_func, emojis):
    # Possible rewards:
    solosd = [38, 34, 30, 26, 22, 18, 14, 10, 6, 2]
    duosd = [34, 26, 18, 10, 2]
    three = {'victory': [33, 30], 'draw': [15], 'defeat': [5]}
    # Colors
    win = 0x00bd5b
    draw = 0x1071e0
    loss = 0xd60606
    # Power Play
    pptrophy_emoji = str(get_emoji(emojis, name='pptrophy'))
    pp_channel = channel_func(720098854887882845)
    # Today
    today = (datetime.utcnow() - timedelta(hours=2)).date()
    # Open tracking members
    with open('pptracking.json') as f:
        players = load(f)['players']
    # Search (unoptimized)
    for playertag in players:
        fulltag = '#' + playertag
        # Battlelog in chronological order (first is earliest)
        battlelog = get_battlelog(playertag)['items'][::-1]
        for b in battlelog:
            battledate = battletime(b['battleTime'])
            if battledate < (today - timedelta(days=1)):
                # Battle was fought at least two PP days ago
                # Unnecessary optimization?
                continue
            if 'type' not in b['battle'] or b['battle']['type'] != 'ranked':
                # Type is absent in weekend (aka ticketed) events
                continue
            if battle_exists(b['battleTime'], playertag):
                # Already recorded
                continue
            # Find Trophy Change, set up embed
            trophychange = b['battle'].get('trophyChange', 0)
            mode = camel_to_title(b['event']['mode'])
            bmap = b['event']['map']
            embed = discord.Embed(title="Power Play Match")
            embed.colour = draw
            embed.add_field(name='Mode', value=mode)
            embed.add_field(name='Map', value=bmap)
            embed.add_field(name='\u200b', value='\u200b')
            # Calculate possible results
            if b['event']['mode'] == 'soloShowdown':
                rank = b['battle']['rank']
                if solosd[rank - 1] != trophychange:
                    continue
                # Guaranteed to be new at this point
                brawler = [
                    p['brawler']['name'] for p in players
                    if p['tag'] == fulltag
                ][0]
                embed.add_field(name='Rank', value=rank)
                embed.add_field(
                    name='Result',
                    value=f"{pptrophy_emoji} {trophychange:+}"
                )
                embed.add_field(name='\u200b', value='\u200b')
                embed.add_field(
                    name="Player 1",
                    value=f"#{playertag}\n{brawler}"
                )
                # Need 2 more blanks?
                # Set embed colour
                if rank <= 4:
                    embed.colour = win
                elif rank >= 6:
                    embed.colour = loss
                # Write to DB
                insert_pp(
                    battledate, b['battleTime'], mode, bmap, trophychange,
                    playertag, brawler
                )
            elif b['event']['mode'] == 'duoShowdown':
                rank = b['battle']['rank']
                if duosd[rank - 1] != trophychange:
                    continue
                # Guaranteed to be new at this point
                for t in b['battle']['teams']:
                    team = [
                        t[0]['tag'], t[0]['brawler']['name'],
                        t[1]['tag'], t[1]['brawler']['name']
                    ]
                    if fulltag in team:
                        break
                embed.add_field(name='Rank', value=rank)
                embed.add_field(
                    name='Result',
                    value=f"{pptrophy_emoji} {trophychange:+}"
                )
                embed.add_field(name='\u200b', value='\u200b')
                embed.add_field(
                    name="Player 1",
                    value=f"{team[0]}\n{team[1]}"
                )
                embed.add_field(
                    name="Player 2",
                    value=f"{team[2]}\n{team[3]}"
                )
                # Need 1 more blank?
                # Set embed colour
                if rank <= 2:
                    embed.colour = win
                elif rank >= 4:
                    embed.colour = loss
                # Write to DB
                insert_pp(
                    battledate, b['battleTime'], mode, bmap, trophychange,
                    team[0][1:], team[1], p2tag=team[2][1:], p2brawler=team[3]
                )
            else:
                result = b['battle']['result']
                if trophychange not in three[result]:
                    continue
                # Guaranteed to be new at this point
                for t in b['battle']['teams']:
                    team = [
                        t[0]['tag'], t[0]['brawler']['name'],
                        t[1]['tag'], t[1]['brawler']['name'],
                        t[2]['tag'], t[2]['brawler']['name']
                    ]
                    if fulltag in team:
                        break
                embed.add_field(name='Outcome', value=result)
                embed.add_field(
                    name='Result',
                    value=f"{pptrophy_emoji} {trophychange:+}"
                )
                embed.add_field(name='\u200b', value='\u200b')
                embed.add_field(
                    name="Player 1",
                    value=f"{team[0]}\n{team[1]}"
                )
                embed.add_field(
                    name="Player 2",
                    value=f"{team[2]}\n{team[3]}"
                )
                embed.add_field(
                    name="Player 3",
                    value=f"{team[4]}\n{team[5]}"
                )
                # Set embed colour
                if result == 'victory':
                    embed.colour = win
                elif result == 'defeat':
                    embed.colour = loss
                # Write to DB
                insert_pp(
                    battledate, b['battleTime'], mode, bmap, trophychange,
                    team[0][1:], team[1], p2tag=team[2][1:], p2brawler=team[3],
                    p3tag=team[4][1:], p3brawler=team[5]
                )
            await pp_channel.send(embed=embed)


# BELOW IS MANUAL SEARCH
def search_battlelog(playertag, mode='', bmap=''):
    name = ''
    search_results = []
    # TEMPORARY
    brawlers = []
    tchanges = []
    # Possible rewards:
    solosd = [38, 34, 30, 26, 22, 18, 14, 10, 6, 2]
    duosd = [34, 26, 18, 10, 2]
    three = {'victory': [33, 30], 'draw': [15], 'defeat': [5]}
    # Battlelog in chronological order (first is earliest)
    battlelog = get_battlelog(playertag)['items'][::-1]
    if battlelog is None:
        return ('', None, '')
    for b in battlelog:
        # Required
        if 'type' not in b['battle'] or b['battle']['type'] != 'ranked':
            # Type is absent in ticketed events
            continue
        if mode and b['battle']['mode'] != mode:
            continue
        if bmap and b['event']['map'] != bmap:
            continue
        # Calculate possible results
        if b['event']['mode'] == 'soloShowdown':
            results = solosd
        elif b['event']['mode'] == 'duoShowdown':
            results = duosd
        else:
            results = three
        # Find trophy change, player
        # API has a flaw where if trophyChange is zero, it doesn't show
        if 'trophyChange' in b['battle']:
            trophyChange = int(b['battle']['trophyChange'])
        else:
            trophyChange = 0
        if b['event']['mode'] == 'soloShowdown':
            player = [
                p for p in b['battle']['players'] if p['tag'][1:] == playertag
            ][0]
        else:
            player = [
                p for t in b['battle']['teams']
                for p in t if p['tag'][1:] == playertag
            ][0]
        # Search
        if b['event']['mode'] in ['soloShowdown', 'duoShowdown']:
            rank = b['battle']['rank']
            if results[int(rank)-1] != trophyChange:
                continue
            brawler = player['brawler']['name']
            name = player['name']
            search_results.append(
                f"Rank {rank} ({trophyChange:+}) with {brawler} in "
                f"{camel_to_title(b['event']['mode'])} "
                f"on {b['event']['map']}.")
        else:
            result = b['battle']['result']
            if trophyChange not in results[result]:
                continue
            brawler = player['brawler']['name']
            name = player['name']
            search_results.append(
                f"{result.title()} ({trophyChange:+}) with {brawler} in "
                f"{camel_to_title(b['event']['mode'])} "
                f"on {b['event']['map']}.")
        # TEMP
        brawlers.append(brawler.title())
        tchanges.append(str(trophyChange))
    while len(brawlers) < 3:
        brawlers.append('-')
        tchanges.append('0')
    return (name, search_results[-3:], brawlers[-3:] + tchanges[-3:])


def camel_to_title(phrase):
    return ''.join(' ' + x if x.isupper() else x for x in phrase).title()


async def pp_search(ctx, args):
    # Check mode
    if len(args) == 0:
        mode = ''
    elif args[0].lower() in ['solo', 'solosd', 'ssd', 'soloshowdown']:
        mode = 'soloShowdown'
    elif args[0].lower() in ['duo', 'duosd', 'dsd', 'duoshowdown']:
        mode = 'duoShowdown'
    elif args[0].lower() in ['gg', 'gem', 'gemgrab']:
        mode = 'gemGrab'
    elif args[0].lower() in ['h', 'heist']:
        mode = 'heist'
    elif args[0].lower in ['b', 'bounty']:
        mode = 'bounty'
    elif args[0].lower in ['bb', 'brawl', 'brawlball']:
        mode = 'brawlBall'
    elif args[0].lower in ['s', 'siege']:
        mode = 'siege'
    else:
        await ctx.send("Invalid power play mode!")
        return
    # Check map
    if len(args) >= 2:
        bmap = args[1]
    else:
        bmap = ''
    # Check for tags
    if len(args) >= 3:
        playertags = [tag.upper() for tag in args[2:]]
    else:
        playertags = PPSQUAD
    # TEMP
    fullcsv = []
    # Run search
    for tag in playertags:
        name, search_results, csv = search_battlelog(tag, mode=mode, bmap=bmap)
        if search_results is None:
            await ctx.send(f'{tag} is not a valid playertag.')
        elif search_results:
            await ctx.send(
                f'Recent Power Play history for {name}:\n' +
                '\n'.join(search_results)
            )
        else:
            await ctx.send(
                f"No recent power play results found for {tag}."
            )
        if tag in PPSQUAD:
            fullcsv.extend(csv)
    await ctx.send(f"CSV (use LAlt+D+E): {','.join(fullcsv)}")
