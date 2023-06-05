import discord

class Colors: 
    """Just colors"""
    red = 0xbc9cfc
    green = 0xbc9cfc
    yellow = 0xF4DB6D
    gold = 0xb4baf7
    default = 0xbc9cfc
    rainbow = 0x2f3136

class Emojis:
    """Just emojis"""
    check = "<:haunt_check:1112707847734698015>"
    wrong = "<:haunt_cross:1112707850561650698>"
    warning = "<:haunt_warn:1112707865594036269>"

class Func:
 def ordinal(num: int):
   """Convert from number to ordinal (10 - 10th)""" 
   num = str(num) 
   if num in ["11", "12", "13"]:
       return num + "th"
   if num.endswith("1"):
      return num + "st"
   elif num.endswith("2"):
      return num + "nd"
   elif num.endswith("3"): 
       return num + "rd"
   else: return num + "th"    