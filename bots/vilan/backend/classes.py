class Colors: 
    """Just colors"""
    red = 0x2f3136
    green = 0x2f3136
    yellow = 0x2f3136
    default = 0x2f3136

class Emojis:
    """Just emojis"""
    check = "<:check2:1034791707679666186>"
    wrong = "<:stop:1034791708216533074>"
    warning = "<:warned:1034791706551406592>"

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