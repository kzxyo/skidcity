const Discord = require('discord.js');
const { default_prefix, color } = require("../../config.json");
const { remove } = require('../../emojis.json')
const { deny } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "roleremove",
  aliases: ["rr"],

  run: async (client, message, args) => {
    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };

    if (!message.member.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_roles\`` } });
    if (!message.guild.me.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_roles\`` } });

    const mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]) || message.guild.roles.cache.find(r => r.name === args.slice(1).join(' '));

    const rolehelpEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: roleremove')
      .setDescription('Removes role from a member')
      .addField('**Aliases**', 'rr', true)
      .addField('**Parameters**', 'member, role', true)
      .addField('**Information**', `${warn} Manage Roles`, true)
      .addField('**Usage**', '\`\`\`Syntax: roleremove (member) <role name>\nExample: roleremove four#0001 Owner\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(rolehelpEmbed)
    if (!mentionedMember) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: Please state a role to remove from the user. Run \`${prefix}roleremove\` to view the correct **syntax**` } })

    if (mentionedMember.roles.highest.position >= message.member.roles.highest.position) return message.channel.send({ embed: { color: "#fe6464", description: `${deny} ${message.author}: You cannot remove a role that is **higher** than **yours**` } });
    if (!args[1]) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: Please state a role to remove from the user. Run \`${prefix}roleremove\` to view the correct **syntax**` } })
    if (!role) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: That role **doesn't** exist, state a valid role` } });
    if (message.member.roles.highest.position <= role.position) message.channel.send({ embed: { color: "#fe6464", description: `${deny} ${message.author}: You cannot remove a role that is **higher** than **yours**` } });

    await mentionedMember.roles.remove(role.id).catch(err => console.log(err))
    const rolegiveEmbed = new Discord.MessageEmbed()
      .setDescription(`${remove} ${message.author}: Removed ${role} from ${mentionedMember}`)
      .setColor("#46bcec")
    return message.channel.send(rolegiveEmbed)
  }
}