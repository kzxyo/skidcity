const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "inrole",
  aliases: ['members', 'rolemembers'],
  description: `clean up bot and invoking messages`,
  usage: '{guildprefix}inrole [role]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if (!args[0]) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}inrole`)
      .setDescription('get a list of users in that role')
      .addFields(
      { name: '**usage**', value: `${guildprefix}inrole [role]`, inline: false },
      { name: '**aliases**', value: `members, rolemembers`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.join(' ').toLocaleLowerCase());

    if (!role) return message.channel.send(`i couldn't find that role`)

    let members = message.guild.members.cache.filter(member => {
      return member.roles.cache.find(r => r.name === role.name);
    }).map(member => {
      return member.user;
    })

    if (members < 1) return message.channel.send(`**${role.name}** has no members in the role`)

    if (members > 50) return message.channel.send(`**${role.name}** has too many members to display (${members.size}+)`)

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .addFields(
    { name: `**${role.name}** role members`, value: `${members.join("\n")}`, inline: false },
    )
    .setFooter({ text: `${role.members.size} members` })

    message.channel.send({ embeds: [embed] })
  }
}