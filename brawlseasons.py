"""
All functions related to the Brawl Pass Seasons.
"""

from json import load


""" PROGRESSION VALUES """
BRAWL_BOX = 53.7
BIG_BOX = 3 * BRAWL_BOX


# Returns the time left
def season_reset():
    # Load data
    with open("seasondata.json") as f:
        seasondata = load(f)['seasons'][-1]
    rewards = seasondata['rewards']
    cost = seasondata['cost']
    pass

# Needs reworking
def season_rewards(convert=False, brawlerlist=[]):
    """
    Generates brawl pass rewards from seasondata.json
    First list is F2P track, second is Brawl Pass track, third is token cost
    convert does alternate reward conversion
    brawlerlist is necessary with convert=True
    """
    # Load data
    with open("seasondata.json") as f:
        seasondata = load(f)['seasons'][-1]
    rewards = seasondata['rewards']
    cost = seasondata['cost']

    # Convert stored datatype to progression
    def translate(rewardstring):
        if rewardstring == "":
            return 0
        elif rewardstring[0] == 'b':
            return BRAWL_BOX * int(rewardstring[1:])
        elif rewardstring[0] == 'c':
            return int(rewardstring[1:])
        elif rewardstring[0] == 'p':
            if convert:
                return BIG_BOX
            else:
                return 2 * int(rewardstring[1:])
        elif rewardstring[0] == 'n':
            if convert and rewardstring[1:] in brawlerlist:
                return BIG_BOX
            else:
                return 0
        else:
            return 0

    for r in range(len(rewards)):
        rewards[r] = [translate(s) for s in rewards[r].split('/')]
    return (list(zip(*rewards)), [cost])  # Unzips
