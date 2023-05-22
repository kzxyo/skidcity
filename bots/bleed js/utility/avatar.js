const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "avatar",
  aliases: ["av"],

  run: async (client, message, args) => {
    message.channel.startTyping();

    let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || args[0] || message.member;

    const user = await client.users.fetch(client.users.resolveID(mentionedMember)).catch(() => null);
    if (!user) user = message.author;

    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle(user.username + "'s avatar")
      .setURL(user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setImage(user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setColor(mentionedMember.displayHexColor || color)
      
      message.channel.stopTyping(true);
    message.channel.send(embed);
  }
}