const { MessageEmbed, Permissions } = require('discord.js')
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "jaillist",
  description: "gets all the jailed users",
  usage: '{guildprefix}jaillist',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send(`this command requires \`manage roles\` permission`)

    let members = message.guild.members.cache.filter(member => {
      return member.roles.cache.find(r => r.name === 'jailed');
    }).map(member => {
      return member.user.tag;
    })

    const jailrole = message.guild.roles.cache.find(role => role.name === 'jailed');

    if (!jailrole) return message.channel.send('no jail role exists')

    if (members > 50) return message.channel.send(`there are too many members jailed`)

    if (members < 1) return message.channel.send(`no members are currently in jail..`)

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle(`${message.guild.name}'s jail`)
    .setDescription(`**${members.join("\n")}**`)

    message.channel.send({ embeds: [embed] })
  }
}