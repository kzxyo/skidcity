const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "members",
  aliases: ["inrole"],

  run: async (client, message, args) => {
    if (args.includes("@everyone")) return;

    if (args.includes("@here")) return;

    const inroleEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: members')
      .setDescription('View members in a role')
      .addField('**Aliases**', 'inrole', true)
      .addField('**Parameters**', 'role', true)
      .addField('**Information**', `N/A`, true)
      .addField('**Usage**', '\`\`\`Syntax: members <role>\nExample: members Friends\`\`\`')
      .setFooter(`Module: information`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(inroleEmbed)

    let role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.join(' ').toLocaleLowerCase());
    if (!role) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You need to enter a **valid** role` } });

    let membersWithRole = message.guild.members.cache.filter(member => {
      return member.roles.cache.find(r => r.name === role.name);
    }).map(member => {
      return member.user.tag;
    })
    if (membersWithRole > 2048) return message.channel.send('List is too long')

    let roleListEmbed = new Discord.MessageEmbed()
      .setColor(role.hexColor)
      .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
        dynamic: true,
        size: 2048
      }))
      .setTitle(`Members in '${role.name}'`)
      .setDescription(`**${membersWithRole.join("\n")}**`);
    message.channel.send(roleListEmbed);
  }
}