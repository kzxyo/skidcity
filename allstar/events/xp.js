const { MessageEmbed } = require("discord.js");

const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {
    
      if (message.author.bot) return;
     if (message.partial) return
        let blacklisted = db.get(`blacklisted`)
        if(blacklisted && blacklisted.find(find => find.user == message.author.id)) {
        return;
        }
    let xpsys =  db.get(`xp_${message.guild.id}`)
    if(xpsys) {
      
    
    let ds = db.get(`xp_${message.guild.id}_${message.author.id}`)

    if(message.author.id === '979978940707930143'){
       db.set(`xp_${message.guild.id}_${message.author.id}`,ds + 20)
    } else {
      db.set(`xp_${message.guild.id}_${message.author.id}`,ds + 10)
    }

    if(ds === 500){
      db.set(`level_${message.guild.id}_${message.author.id}`,1)
      message.channel.send({content:`${message.member} you just leveled up to lvl 1`})
    }
    else if(ds === 1000){
      db.set(`level_${message.guild.id}_${message.author.id}`,2)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 2`})
    }
    else if(ds === 2000){
      db.set(`level_${message.guild.id}_${message.author.id}`,3)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 3`})
    }
    else if(ds === 4000){
      db.set(`level_${message.guild.id}_${message.author.id}`,4)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 4`})
    }
    else if(ds === 5000){
      db.set(`level_${message.guild.id}_${message.author.id}`,5)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 5`})
    }
    else if(ds === 7000){
      db.set(`level_${message.guild.id}_${message.author.id}`,6)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 6`})
    }
    else if(ds === 9000){
      db.set(`level_${message.guild.id}_${message.author.id}`,7)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 7`})
    }
        else if(ds === 12000){
      db.set(`level_${message.guild.id}_${message.author.id}`,8)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 8`})
    }
        else if(ds === 15000){
      db.set(`level_${message.guild.id}_${message.author.id}`,9)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 9`})
    }
        else if(ds === 18000){
      db.set(`level_${message.guild.id}_${message.author.id}`,10)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 10`})
    }
        else if(ds === 20000){
      db.set(`level_${message.guild.id}_${message.author.id}`,11)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 11`})
    }
        else if(ds === 24000){
      db.set(`level_${message.guild.id}_${message.author.id}`,12)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 12`})
    }
            else if(ds === 28000){
      db.set(`level_${message.guild.id}_${message.author.id}`,13)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 13`})
    }
        else if(ds === 33000){
      db.set(`level_${message.guild.id}_${message.author.id}`,14)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 14`})
    }
        else if(ds === 38000){
      db.set(`level_${message.guild.id}_${message.author.id}`,15)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 15`})
    }
            else if(ds === 44000){
      db.set(`level_${message.guild.id}_${message.author.id}`,16)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 16`})
    }
            else if(ds === 50000){
      db.set(`level_${message.guild.id}_${message.author.id}`,17)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 17`})
    }
            else if(ds === 55000){
      db.set(`level_${message.guild.id}_${message.author.id}`,18)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 18`})
    }
            else if(ds === 60000){
      db.set(`level_${message.guild.id}_${message.author.id}`,19)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 19`})
    }
            else if(ds === 70000){
      db.set(`level_${message.guild.id}_${message.author.id}`,20)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 20`})
    }
            else if(ds === 85000){
      db.set(`level_${message.guild.id}_${message.author.id}`,21)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 21`})
    }
            else if(ds === 100000){
      db.set(`level_${message.guild.id}_${message.author.id}`,22)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 22`})
    }
            else if(ds === 120000){
      db.set(`level_${message.guild.id}_${message.author.id}`,23)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 23`})
    }
                else if(ds === 150000){
      db.set(`level_${message.guild.id}_${message.author.id}`,24)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 24`})
    }
                else if(ds === 200000){
      db.set(`level_${message.guild.id}_${message.author.id}`,25)
      return message.channel.send({content:`${message.member} you just leveled up to lvl 25`})
    }
                else if(ds === 250000){
      db.set(`level_${message.guild.id}_${message.author.id}`,26)
      return message.channel.send({content:`${message.member}: you just leveled up to lvl 26`})
    }
                else if(ds === 300000){
      db.set(`level_${message.guild.id}_${message.author.id}`,27)
      return message.channel.send({content:`${message.member}: you just leveled up to lvl 27`})
    }
                else if(ds === 350000){
      db.set(`level_${message.guild.id}_${message.author.id}`,28)
      return message.channel.send({content:`${message.member}: you just leveled up to lvl 28`})
    }
                else if(ds === 400000){
      db.set(`level_${message.guild.id}_${message.author.id}`,29)
      return message.channel.send({content:`${message.member}: you just leveled up to lvl 29`})
    }
                else if(ds === 450000){
      db.set(`level_${message.guild.id}_${message.author.id}`,30)
      return message.channel.send({content:`${message.member}: you just leveled up to lvl 30`})
    }              else if(ds === 550000){
        db.set(`level_${message.guild.id}_${message.author.id}`,31)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 31`})
      }              else if(ds === 650000){
        db.set(`level_${message.guild.id}_${message.author.id}`,32)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 32`})
      }              else if(ds === 800000){
        db.set(`level_${message.guild.id}_${message.author.id}`,33)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 33`})
      }              else if(ds === 950000){
        db.set(`level_${message.guild.id}_${message.author.id}`,34)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 34`})
      }              else if(ds === 1200000){
        db.set(`level_${message.guild.id}_${message.author.id}`,35)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 35`})
      }              else if(ds === 1500000){
        db.set(`level_${message.guild.id}_${message.author.id}`,36)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 36`})
      }              else if(ds === 2000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,37)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 37`})
      }              else if(ds === 2500000){
        db.set(`level_${message.guild.id}_${message.author.id}`,38)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 38`})
      }              else if(ds === 3000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,39)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 39`})
      }              else if(ds === 4500000){
        db.set(`level_${message.guild.id}_${message.author.id}`,40)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 40`})
      }              else if(ds === 6500000){
        db.set(`level_${message.guild.id}_${message.author.id}`,41)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 41`})
      }              else if(ds === 9000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,42)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 42`})
      }              else if(ds === 10000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,43)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 43`})
      }              else if(ds === 12000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,44)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 44`})
      }              else if(ds === 15000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,45)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 45`})
      }              else if(ds === 20000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,46)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 46`})
      }              else if(ds === 25000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,47)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 47`})
      }              else if(ds === 35000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,48)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 48`})
      }              else if(ds === 55000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,49)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 49`})
      }              else if(ds === 100000000){
        db.set(`level_${message.guild.id}_${message.author.id}`,50)
        return message.channel.send({content:`${message.member}: you just leveled up to lvl 50`})
      }
    
    } else return;
    
    
    
  },
};