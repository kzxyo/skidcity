import discord

class Colors: 
    """Just colors"""
    red = 0x2f3136
    green = 0x2f3136
    yellow = 0x2f3136
    gold = 0xb4baf7
    default = 0x2f3136
    rainbow = 0x2f3136

class Emojis:
    """Just emojis"""
    check = "<:abortapprove:1105356064200851546>"
    wrong = "<:abortdeny:1105355887050248243>"
    warning = "<:abortwarn:1114218743170613320>"

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