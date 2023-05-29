class Colors: 
    """Just colors"""
    red = 0x2f3136
    green = 0x2f3136
    yellow = 0x2f3136
    default = 0x495063

class Emojis:
    """Just emojis"""
    check = "<:emoji_7:1067261311026741340>"
    wrong = "<:error:1067261128708730940>"
    warning = "<:warned:1066032289806557198>"

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