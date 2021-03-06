"""
All functions designed to do simple, repetitive calculations.
"""


""" GAME CONSTANTS """
#        0  1   2   3   4    5    6    7    8    9  10
POINTS = [0, 20, 30, 50, 80, 130, 210, 340, 550, 0, 0]
COINS = [0, 20, 35, 75, 140, 290, 480, 800, 1250, 0, 0]
RESETDATA = [
    #From, to, SP
    [501, 500, 20],
    [525, 524, 50],
    [550, 549, 70],
    [575, 574, 80],
    [600, 599, 90],
    [625, 624, 100],
    [650, 649, 110],
    [675, 674, 120],
    [700, 699, 130],
    [725, 724, 140],
    [750, 749, 150],
    [775, 774, 160],
    [800, 799, 170],
    [825, 824, 180],
    [850, 849, 190],
    [875, 874, 200],
    [900, 885, 210],
    [925, 900, 220],
    [950, 920, 230],
    [975, 940, 240],
    [1000, 960, 250],
    [1050, 980, 260],
    [1100, 1000, 270],
    [1150, 1020, 280],
    [1200, 1040, 290],
    [1250, 1060, 300],
    [1300, 1080, 310],
    [1350, 1100, 320],
    [1400, 1120, 330],
    [1450, 1140, 340],
    [1500, 1150, 350],
    # Old
    # [550, 525, 70],
    # [600, 575, 120],
    # [650, 625, 160],
    # [700, 650, 200],
    # [750, 700, 220],
    # [800, 750, 240],
    # [850, 775, 260],
    # [900, 825, 280],
    # [950, 875, 300],
    # [1000, 900, 320],
    # [1050, 925, 340],
    # [1100, 950, 360],
    # [1150, 975, 380],
    # [1200, 1000, 400],
    # [1250, 1025, 420],
    # [1300, 1050, 440],
    # [1350, 1075, 460],
    # [1400, 1100, 480],
    [10000, 0, 0]
]
PPDATA = [
    #Up to, reward
    [0, 0],
    [99, 25],
    [149, 50],
    [199, 100],
    [249, 150],
    [299, 200],
    [349, 250],
    [399, 300],
    [449, 350],
    [499, 400],
    [549, 450],
    [599, 500],
    [649, 550],
    [699, 600],
    [749, 700],
    [799, 800],
    [849, 1000],
    [899, 1500],
    [949, 2000],
    [999, 2500],
    [1049, 3000],
    [1099, 4000],
    [1149, 5000],
    [1199, 6000],
    [1249, 8000],
    [10000, 10000]
]

# Returns the trophy loss and starpoints from trophy reset
def trophy_reset(trophies):
    # Returns (trophy_loss, starpoints)
    if trophies < RESETDATA[0][0]:
        return (0, 0)
    index = 0
    while trophies >= RESETDATA[index+1][0]:
        index += 1
    return (trophies - RESETDATA[index][1], RESETDATA[index][2])

# Convert total points to display points, and returns points for next level
def points_to_display(points, level):
    # Returns (display points, points to next level)
    return (max(0, points - sum(POINTS[:level])), POINTS[level])

# Convert display points to total points
def display_to_points(points, level):
    # Returns total points
    return points + sum(POINTS[:level])

# Returns starpoints from power play trophies
def pp_reset(pptrophies):
    index = 0
    while pptrophies > PPDATA[index][0]:
        index += 1
    return PPDATA[index][1]

# Returns points and coins remaining
def prog_remaining(level):
    # Returns (points, coins)
    return (sum(POINTS) - sum(POINTS[:level]), sum(COINS) - sum(COINS[:level]))
