const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "guildbanner",
  aliases: ["gbanner", "serverbanner"],
  category: "utility",

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    const bannerEmbed = new Discord.MessageEmbed()

      .setColor(mentionedMember.displayHexColor || color)
      .setTitle(`${message.guild.name}'s guild banner`)
      .setImage(message.guild.bannerURL({
        dynamic: true,
        format: "png",
        size: 2048
      }))

    return message.channel.send(bannerEmbed)
  }
}