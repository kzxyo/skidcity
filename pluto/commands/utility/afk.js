const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')
const afkschema = require('../../database/afk')

module.exports = {
  name: "afk",
  description: `sets afk status`,
  usage: '{guildprefix}afk\n{guildprefix}afk [reason]',
  run: async(client, message, args) => {

    const content = args.join(" ") ? args.join(' ') : "AFK"

    afkschema.findOne({ GuildID: message.guild.id, UserID: message.author.id }, async(err, data) => {
    
      if(data) {

        return;
      
      } else {

        let afkdata = new afkschema({
          GuildID: message.guild.id,
          UserID: message.author.id,
          Message: content,
          TimeAgo: Date.now()
        })

        afkdata.save()
        
        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setAuthor({ name: `${message.author.username + " is now afk with the status.."}`, iconURL: `${message.author.displayAvatarURL({ dynamic: true })}` })
        .setDescription(`> ${content}`)
        
        return message.channel.send({ embeds: [embed] })
      }
    })    
  }
}