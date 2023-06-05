import discord

class Colors: 
    """Just colors"""
    red = 0xbc9cfc
    green = 0xbc9cfc
    yellow = 0xbc9cfc
    gold = 0xb4baf7
    default = 0xbc9cfc
    rainbow = 0x2f3136

class Emojis:
    """Just emojis"""
    check = "<:success:1108885091595333673>"
    wrong = "<:deny:1109821067096236052>"
    warning = "<:warn:1109820995092611254>"
    remove  = "<:remove:1108885089846300774>"
    add = "<:add:1108885082372051006>"

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