const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')
const moment = require('moment')

module.exports = {
  name: "roleinfo",
  aliases: ["rinfo"],

  run: async (client, message, args) => {
    const roleInfoEmbed2 = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: roleinfo')
      .setDescription('View information about a role')
      .addField('**Aliases**', 'rinfo', true)
      .addField('**Parameters**', 'role', true)
      .addField('**Information**', `N/A`, true)
      .addField('**Usage**', '\`\`\`Syntax: roleinfo <role>\nExample: roleinfo Friends\`\`\`')
      .setFooter(`Module: information`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(roleInfoEmbed2)
    let role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.join(' ').toLocaleLowerCase());
    if (!role) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You need to enter a **valid** role` } });

    const roleInfoEmbed = new Discord.MessageEmbed()
      .setColor(role.hexColor)
      .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
        dynamic: true,
        size: 2048
      }))
      .setTitle(`${role.name}`)
      .addField("**Role ID**", `\`${role.id}\``, true)
      .addField("**Guild**", `${message.guild.name} (\`${message.guild.id}\`)`, true)
      .addField("**Hex**", `\`${role.hexColor}\``, true)
      .addField("**Creation Date**", `${moment(role.createdAt).format("dddd, MMMM Do YYYY, h:mm A")}`, false)
      .addField(`**${role.members.size} Member(s)**`, role.members.size, false)

    message.channel.send(roleInfoEmbed);
  }
}