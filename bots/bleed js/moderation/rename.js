const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "rename",
  aliases: ["nick"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\`` } });

    const mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    const nickEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: rename')
      .setDescription('Assigns the mentioned user a new nickname in the guild')
      .addField('**Aliases**', 'nick', true)
      .addField('**Parameters**', 'member, reason', true)
      .addField('**Information**', `${warn} Ban Members`, true)
      .addField('**Usage**', '\`\`\`Syntax: rename (member) <new nick>\nExample: rename four#0001 amir\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(nickEmbed)

    if (mentionedMember.roles.highest.position >= message.member.roles.highest.position) return message.channel.send({ embed: { color: "#fe6464", description: `${deny} ${message.author}: You can't **rename** someone who is **higher** than you` } });

    let user = message.mentions.users.first();
    if (!user) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You need to **mention** a user` } });

    let nick = args.slice(1).join(" ");
    if (!nick) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You need to **input** a nickname` } });

    let member = message.guild.members.cache.get(user.id);

    await member.setNickname(nick);
    return message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Changed **${user.username}**'s nickname to \`${nick}\`` } });
  }
}