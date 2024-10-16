const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "jail",
  description: `jails the specified member (sets up upon first use)`,
  usage: '{guildprefix}jail [member]\n{guildprefix}jail [member] [reason]',
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
      .setTitle(`${guildprefix}jail`)
      .setDescription('jails the specified member (sets up upon first use)')
      .addFields(
      { name: '**usage**', value: `${guildprefix}jail [user]\n${guildprefix}jail [user] [reason]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const jailrole = message.guild.roles.cache.find(role => role.name === 'jailed');

    const jailchannel = message.guild.channels.cache.find(c => c.name === 'jail')

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

    if (!jailchannel) {

      let jailcreate = await message.guild.channels.create('jail', {
          type: 'GUILD_TEXT',
          permissionOverwrites: [{
            id: message.guild.id,
            deny: ['VIEW_CHANNEL'],
          }]
        })
      jailcreate.setPosition(0).catch(() => {
        return message.channel.send(`an error occured`)
      })
    }

    const jailrole2 = message.guild.roles.cache.find(role => role.name === 'jailed');

    const jailchannel2 = message.guild.channels.cache.find(c => c.name === 'jail')

    jailchannel2.permissionOverwrites.edit(message.guild.id, {
      VIEW_CHANNEL: false,
    }).catch(() => { return; })

    jailchannel2.permissionOverwrites.edit(jailrole2, {
      VIEW_CHANNEL: true,
      SEND_MESSAGES: true,
      MENTION_EVERYONE: false
    }).catch(() => { return; })

    if(user === message.member) return message.channel.send(`jail yourself.. loser..`)

    if (jailrole2.position >= message.member.roles.highest?.position) return message.channel.send(`put my role above the jail role`)

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send('you cant jail someone above your role')

    if (user.roles.cache.has(jailrole2?.id)) return message.channel.send('user is already jailed')

    user.roles.add(jailrole2.id).then(() => {
      
      message.channel.send(`**${user.user.tag}** has been jailed 👍`)

      jailchannel2.send(`${user}, you've been jailed, contact staff about your punishment 👍`)
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}