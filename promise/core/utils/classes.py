import discord

class Colors: 
    """Just colors"""
    red = 0x9A8A8B
    green = 0x9A8A8B
    yellow = 0x9A8A8B
    default = 0x9A8A8B

class Emojis:
    """Just emojis"""
    check = "<:1woostargrey:1074749582673723524>"
    wrong = "<:1woostargrey:1074749582673723524>"
    warning = "<:1woostargrey:1074749582673723524>"

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
