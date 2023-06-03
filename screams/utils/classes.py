class colors: 
    default = 0xb19cd9
    invis = 0x2f3136

class emojis:
    warn = "<:x_warn:1059195228390699140>"
    approve = "<:x_approve:1059195198309159012>"
    bigwarn = "<:x_warn:1059195228390699140>"

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