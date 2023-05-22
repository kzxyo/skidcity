const { MessageEmbed } = require("discord.js");
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
const ms = require('moment');
const talkedRecently = new Set();
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {


  if (message.partial) return
  if (message.author.bot) return;
    let tim = db.get(`afktime-${message.author.id}+${message.guild.id}`)
  if (db.has(`afk-${message.author.id}+${message.guild.id}`)) {
          const embed2 = new MessageEmbed()
        .setColor(color)
        .setDescription(`<a:allstarwelcome:996512695480238182>  Welcome back ${message.author.tag} `) // + db.get(`afk-${message.author.id}+${message.guild.id}`)
        .setFooter({text:`last seen ${ms(tim).fromNow()}`})

          const info = db.get(`afk-${message.author.id}+${message.guild.id}`)
    await db.delete(`afk-${message.author.id}+${message.guild.id}`)
    message.reply({ embeds:[embed2]});
  }
    
                if (talkedRecently.has(message.author.id)) {
    } else {

  if (message.mentions.members.first()) {
    if (db.has(`afk-${message.mentions.members.first().id}+${message.guild.id}`)) {
      let time = db.get(`afktime-${message.mentions.members.first().id}+${message.guild.id}`)
      const embed = new MessageEmbed()
        .setColor(error)
        .setDescription(` <:warn:1033072412188737638>  ${message.mentions.members.first()} is AFK: \n <:allstarreply:1032192256192553030>  ` + db.get(`afk-${message.mentions.members.first().id}+${message.guild.id}`))
        .setFooter({text:`last seen ${ms(time).fromNow()}`})
      message.reply({embeds:[embed]})
    } else return;
  } else;
    
    }



    
              talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 47000);
    

    
  },
};