const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "unjail",
  description: `unjails the specified member`,
  usage: '{guildprefix}unjail [member]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send(`this command requires \`manage roles\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send(`this command requires me to have \`manage roles\` permission`)

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) {
      
      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}unjail`)
      .setDescription('unjails the specified member')
      .addFields(
      { name: '**usage**', value: `${guildprefix}unjail [member]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if(user === message.member) return message.channel.send(`jail yourself.. loser..`)

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send('you cant jail someone above your role')

    const jailrole = message.guild.roles.cache.find(role => role.name === 'jailed');

    if(!jailrole) {

      const jailrole = await message.guild.roles.create({
        name: 'jailed',
        color: 'DEFAULT',
      }).then(() => {
        return message.channel.send('setting up jail for the first time..')
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })
    }

    const jailrole2 = message.guild.roles.cache.find(role => role.name === 'jailed');

    if (jailrole2.position >= message.member.roles.highest.position) return message.channel.send(`put my role above the jail role`)

    if (!user.roles.cache.has(jailrole2?.id)) return message.channel.send(`user is not jailed`)

    user.roles.remove(jailrole2.id).then(() => {
      
      message.channel.send(`**${user.user.tag}** has been unjailed 👍`)

    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}