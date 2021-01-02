"""
All functions related to the Trophy League and personal statistics.
"""

from math import ceil

import discord
from discord.utils import get as get_emoji

import bot0
import bsmath
import brawltime


""" GAME CONSTANTS """
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
    ('BEA', 'EPIC'), ('NANI', 'EPIC'), ('EDGAR', 'EPIC'),
    ('MORTIS', 'MYTHIC'), ('TARA', 'MYTHIC'), ('GENE', 'MYTHIC'),
    ('MAX', 'MYTHIC'), ('MR. P', 'MYTHIC'), ('SPROUT', 'MYTHIC'),
    ('BYRON', 'MYTHIC'), ('SPIKE', 'LEGENDARY'), ('CROW', 'LEGENDARY'),
    ('LEON', 'LEGENDARY'), ('SANDY', 'LEGENDARY'), ('AMBER', 'LEGENDARY'),
    ('GALE', 'CHROMATIC'), ('SURGE', 'CHROMATIC'), ('COLETTE', 'CHROMATIC'),
    ('LOU', 'CHROMATIC')
] # Should ping me if brawler is not in this list


async def check_missing_brawler(ctx, all_brawlers=None):
    if all_brawlers is None:
        all_brawlers = bot0.get_all_brawlers()
    if len(all_brawlers) > len(BRAWLER_ORDER):
        missing = [
            b["name"] for b in all_brawlers
            if b["name"] not in list(zip(*BRAWLER_ORDER))[0]
        ]
        await ctx.send(
            f"<@!278589912184258562> Brawler list is missing "
            f"{', '.join(missing)}"
        )

def find_brawler(name, blist):
    for b in blist:
        if b['name'] == name:
            return b
    return None

async def display_levels(ctx, args, emojis):
    player = ctx.message.author
    playerid = bot0.id(player)
    brawltag = bot0.get_brawltag(playerid)
    if brawltag is None:
        await bot0.request_brawltag(ctx)
        return
    playerdata = bot0.get_playerdata(brawltag)
    all_brawlers = bot0.get_all_brawlers()
    await check_missing_brawler(ctx, all_brawlers=all_brawlers)
    # Prepare items to print
    lock_emoji = str(get_emoji(emojis, name='locked'))
    levels = []
    spga = []
    sp_emoji = str(get_emoji(emojis, name='sp'))
    nosp_emoji = str(get_emoji(emojis, name='nosp'))
    ga_emoji = str(get_emoji(emojis, name='ga'))
    noga_emoji = str(get_emoji(emojis, name='noga'))
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
            for sp in max_b['starPowers']:
                if sp in b['starPowers']:
                    icons.append(sp_emoji)
                else:
                    icons.append(nosp_emoji)
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
            icon_url=bot0.profile_icon(
                str(playerdata['icon']['id']), player.avatar_url
            )
        )
        for index in range(
                B_PER_PAGE*p,
                min(B_PER_PAGE*(p+1), len(BRAWLER_ORDER))):
            if levels[index] != '0':
                value = f"Power {levels[index]}\n"
                value += ''.join(spga[index])
                value += '\u0009\u200b\n\u200b'
            else:
                value = f"Locked\n{lock_emoji}\n\u200b"
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
    playerid = bot0.id(player)
    brawltag = bot0.get_brawltag(playerid)
    if brawltag is None:
        await bot0.request_brawltag(ctx)
        return
    playerdata = bot0.get_playerdata(brawltag)
    all_brawlers = bot0.get_all_brawlers()
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
        icon_url=bot0.profile_icon(
            str(playerdata['icon']['id']), player.avatar_url
        )
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
    playerid = bot0.id(player)
    brawltag = bot0.get_brawltag(playerid)
    if brawltag is None:
        await bot0.request_brawltag(ctx)
        return
    playerdata = bot0.get_playerdata(brawltag)
    all_brawlers = bot0.get_all_brawlers()
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
        icon_url=bot0.profile_icon(
            str(playerdata['icon']['id']), player.avatar_url
        )
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

async def profile(ctx, args, emojis):
    player = ctx.message.author
    playerid = bot0.id(player)
    brawltag = bot0.get_brawltag(playerid)
    if brawltag is None:
        await bot0.request_brawltag(ctx)
        return
    playerdata = bot0.get_playerdata(brawltag)
    all_brawlers = bot0.get_all_brawlers()
    # Emoji search
    trophy_emoji = str(get_emoji(emojis, name='trophy'))
    rank_emoji = str(get_emoji(emojis, name='rank'))
    stp_emoji = str(get_emoji(emojis, name='starpoints'))
    pptrophy_emoji = str(get_emoji(emojis, name='pptrophy'))
    log_emoji = str(get_emoji(emojis, name='battlelog'))
    sp_emoji = str(get_emoji(emojis, name='sp'))
    ga_emoji = str(get_emoji(emojis, name='ga'))
    # Embed
    embed = discord.Embed()
    if 'nameColor' in playerdata:
        embed.colour = int(playerdata['nameColor'][4:], base=16)
    embed.set_author(
        name=f"{player.name} #{brawltag}",
        icon_url=bot0.profile_icon(
            str(playerdata['icon']['id']), player.avatar_url
        )
    )
    # Brawler iteration
    total_rank = 0
    maximal_trophies = 0
    num_sp = 0
    num_ga = 0
    total_trophy_loss = 0
    total_starpoints = 0
    for b in playerdata['brawlers']:
        total_rank += b['rank']
        maximal_trophies += b['highestTrophies']
        num_sp += len(b['starPowers'])
        num_ga += len(b['gadgets'])
        trophy_loss, starpoints = bsmath.trophy_reset(b['trophies'])
        total_trophy_loss += trophy_loss
        total_starpoints += starpoints
    total_sp = 0
    total_ga = 0
    for b in all_brawlers:
        total_sp += len(b['starPowers'])
        total_ga += len(b['gadgets'])
    # Data Validation
    trophies = playerdata.get('trophies', 0)
    highest_trophies = playerdata.get('highestTrophies', 0)
    num_brawlers = len(playerdata.get('brawlers', []))
    pp_points = playerdata.get('powerPlayPoints', 0)
    highest_pp_points = playerdata.get('highestPowerPlayPoints', 0)
    # Trophies
    embed.add_field(
        name='Trophies',
        value=(
            f"Current: {trophy_emoji} {trophies}\n"
            f"Highest: {trophy_emoji} {highest_trophies}\n"
            f"Total Rank: {rank_emoji} {total_rank}\n"
            f"Average Rank: {rank_emoji} {total_rank/num_brawlers:.01f}\n"
            f"Individual Max: {trophy_emoji} {maximal_trophies}"
        ),
        inline=False
    )
    # Trophy League
    embed.add_field(
        name='Trophy League',
        value=(
            f"Remaining Trophies: {trophy_emoji} "
            f"{playerdata['trophies'] - total_trophy_loss}\n"
            f"Trophy Loss: {trophy_emoji} {total_trophy_loss}\n"
            f"Reward: {stp_emoji} {total_starpoints}\n"
            f"Time left: :clock3: {brawltime.time_remaining('trophies')}"
        ),
        inline=False
    )
    # Power Play
    embed.add_field(
        name='Power Play',
        value=(
            f"Trophies: {pptrophy_emoji} {pp_points}\n"
            f"Reward: {stp_emoji} {bsmath.pp_reset(pp_points)}\n"
            f"Highest: {pptrophy_emoji} {highest_pp_points}\n"
            f"Time left: :clock3: {brawltime.time_remaining('powerplay')}"
        ),
        inline=False
    )
    # Brawl Pass Season (Retired)
    # embed.add_field(
    #     name=brawltime.season_name(),
    #     value=(
    #         f"Time left: :clock3: {brawltime.time_remaining('brawlpass')}"
    #     ),
    #     inline=False
    # )
    # Unlocked (Brawlers, SP, GA)
    embed.add_field(
        name='Progress',
        value=(
            f"{log_emoji} {num_brawlers}/{len(all_brawlers)}\n"
            f"{sp_emoji} {num_sp}/{total_sp}\n"
            f"{ga_emoji} {num_ga}/{total_ga}\n"
        ),
        inline=False
    )
    await ctx.send(embed=embed)
