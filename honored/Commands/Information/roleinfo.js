const Discord = require('discord.js');
const moment = require('moment');


module.exports = {
  configuration: {
    commandName: "roleinfo",
    aliases: ["rinfo"],
    description: "View information about a role",
    syntax: 'roleinfo',
    example: 'roleinfo',
    permissions: 'N/A',
    parameters: 'role',
    module: 'information',
    devOnly: false
  },

  run: async (session, message, args) => {
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
      .setColor(session.color);

    if (!args[0]) return message.channel.send({ embeds: [roleInfoEmbed2] });

    let role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.join(' ').toLocaleLowerCase());
    if (!role) return message.channel.send({ embeds: [
        new Discord.MessageEmbed()
        .setColor(session.warn)
        .setDescription(`${session.mark} ${message.author}: Role not found`)
    ]})

    const memberMentions = role.members.size > 10 ? role.members.map(member => member.toString()).slice(0, 10).join(', ') : role.members.map(member => member.toString()).join(', ');

    const roleInfoEmbed = new Discord.MessageEmbed()
      .setColor(role.hexColor)
      .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true, size: 2048 }))
      .setTitle(role.name)
      .addField("**Role ID**", `\`${role.id}\``, true)
      .addField("**Guild**", `${message.guild.name} (\`${message.guild.id}\`)`, true)
      .addField("**Hex**", `\`${role.hexColor}\``, true)
      .addField("**Creation Date**", moment(role.createdAt).format("dddd, MMMM Do YYYY, h:mm A"), false)
      .addField(`**${role.members.size} Member(s)**`, memberMentions, false);

    message.channel.send({ embeds: [roleInfoEmbed] });
  }
};
