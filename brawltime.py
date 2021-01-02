"""
All functions related to reset timers.
"""

from datetime import datetime, timedelta
from json import load

""" GAME VARIABLES """
SEASON_OFFSET = 5
TROPHY_LEAGUE_RESET_EPOCH = datetime(2020, 12, 14, 4)
TROPHY_LEAGUE_SEASON_LENGTH = timedelta(weeks=4)
POWER_PLAY_EPOCH = datetime(2020, 5, 11, 22)
POWER_PLAY_SEASON_LENGTH = timedelta(weeks=2)


def season_name():
    with open("seasondata.json") as f:
        return load(f)['seasons'][-1]['name']


def time_remaining(seasontype):
    """
    Prints the time remaining until the season ends.
    Seasontype is one of "brawlpass", "trophies", "powerplay"
    """
    if seasontype == "brawlpass":
        with open("seasondata.json") as f:
            seasondata = load(f)['seasons'][-1]
        date = seasondata['seasonend']
        season_end = datetime(date[0], date[1], date[2], SEASON_OFFSET)
        remaining = season_end - datetime.now()
    else:
        if seasontype == "trophies":
            next_reset = TROPHY_LEAGUE_RESET_EPOCH
            season_length = TROPHY_LEAGUE_SEASON_LENGTH
        elif seasontype == "powerplay":
            next_reset = POWER_PLAY_EPOCH
            season_length = POWER_PLAY_SEASON_LENGTH
        else:
            print("Invalid input")
            return None
        while next_reset < datetime.now():
            next_reset += season_length
        remaining = next_reset - datetime.now()
    days = int(remaining / timedelta(days=1))
    hours = int(remaining / timedelta(hours=1)) % 24
    mins = int(remaining / timedelta(minutes=1)) % 60
    return f"{days}d {hours}h {mins}m"
