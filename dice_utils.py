import re
from random import randint

DICE_PATTERN = r""

def parse_dice_roll(message):
    dice_roll = re.search(r"(\d+d\d+(?:kh\d+|lh\d+)?(\+\d+)?)", message)
    if dice_roll:
        dice_roll = dice_roll.group(1)
    else:
        dice_roll = ""
    return dice_roll

def roll_dice(dice_roll):
    match = re.search(r"(\d+)d(\d+)((kh|lh)\d+)?([+-]\d+)?", dice_roll)
    num_dice = int(match.group(1))
    num_sides = int(match.group(2))
    adv_dis = match.group(3)
    modifier = int(match.group(5)) if match.group(5) else 0
    
    rolls = [randint(1, num_sides) for _ in range(num_dice)]
    
    if adv_dis:
        keep = int(adv_dis[2:])
        if adv_dis.startswith("kh"):
            rolls = sorted(rolls, reverse=True)[:keep]
        elif adv_dis.startswith("lh"):
            rolls = sorted(rolls)[:keep]
    
    total = sum(rolls) + modifier
    return total

def create_dice_result_message(dice_roll, roll_result):
    if dice_roll:
        result_message = f"Rolled: {dice_roll} -> Result: {roll_result}"
    else:
        result_message = ""
    return result_message

def get_dice_result(message):
    dice_roll = parse_dice_roll(message)
    if dice_roll:
        roll_result = roll_dice(dice_roll)
        return create_dice_result_message(dice_roll, roll_result)
    else:
        return ""