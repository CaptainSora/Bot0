from bot0 import get_battlelog
from pprint import pprint

PPSQUAD = ['JQU8Y00R', '22GV9VL', 'UULVQY2L']

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
        return ('', None)
    for b in battlelog:
        # Required
        if b['battle']['type'] != 'ranked':
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
