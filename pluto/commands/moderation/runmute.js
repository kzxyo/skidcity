const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "runmute",
  description: `runmute a user`,
  usage: '{guildprefix}runmute [user]\n{guildprefix}runmute [user] [reason]',
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

    let reason = args.slice(1).join(" ");

    if (!reason) reason = 'n/a'

    const muterole = message.guild.roles.cache.find(role => role.name === 'rmuted');

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}runmute`)
      .setDescription(`runmute a user`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}rmute [user]\n${guildprefix}runmute [user] [reason]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if(user === message.member) return message.channel.send(`you can't runmute yourself`) 

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`you can't runmute someone above you`)

    if(!muterole) { 
      
      const muterole = await message.guild.roles.create({
        name: 'rmuted',
        color: 'DEFAULT',
      }).then(() => {
        return message.channel.send('setting up rmute for the first time..')
      }).catch(() => {
        return message.channel.send('an error occured')         
      })
        
      message.guild.channels.cache.forEach(async (channel) => {
        await channel.permissionOverwrites.edit(muterole, {
          USE_EXTERNAL_EMOJIS: true,
          ADD_REACTIONS: true,
        }).catch(() => {
          return message.channel.send('an error occured')         
        })
      })
    }

    const muterole1 = message.guild.roles.cache.find(role => role.name === 'rmuted');

    if (!user.roles.cache.has(muterole1?.id)) return message.channel.send('user is already runmute')

    user.roles.remove(muterole1.id, reason).then(() => {
      return message.channel.send(`**${user.user.tag}** has been runmuted 👍`)
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}