const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "membercount",
  aliases: ["mc"],
  category: "information",

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;
    
    const botCount = message.guild.members.cache.filter(m => m.user.bot).size;

    const membercountEmbed = new Discord.MessageEmbed()
      .setColor(mentionedMember.displayHexColor || color)
      .setAuthor(`${message.guild.name} statistics`, message.guild.iconURL({
        dynamic: true
      }))
      .setTimestamp()
      .addFields(
        {
          name: "**Users**",
          value: `${message.guild.memberCount}`,
          inline: true
        },
        {
          name: "**Humans**",
          value: `${message.guild.memberCount - botCount}`,
          inline: true
        },

        {
          name: "**Bots**",
          value: `${botCount}`,
          inline: true
        },
      )

    return message.channel.send(membercountEmbed)
  }
}