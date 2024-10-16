const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "mute",
  aliases: ['m'],
  description: `mute a user`,
  usage: '{guildprefix}mute [user]\n{guildprefix}mute [user] [reason]',
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

    const muterole = message.guild.roles.cache.find(role => role.name === 'muted');

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}mute`)
      .setDescription(`mute a user`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}mute [user]\n${guildprefix}mute [user] [reason]`, inline: false },
      { name: '**aliases**', value: `m`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if(user === message.member) return message.channel.send(`you can't mute yourself`) 

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`you can't mute someone above you`)

    if(!muterole) { 
      
      const muterole = await message.guild.roles.create({
        name: 'muted',
        color: 'DEFAULT',
      }).then(() => {
        return message.channel.send('setting up mute for the first time..')
      }).catch(() => {
        return message.channel.send('an error occured')         
      })
        
      message.guild.channels.cache.forEach(async (channel) => {
        await channel.permissionOverwrites.edit(muterole, {
          EMBED_LINKS: false,
          ATTACH_FILES: false,
        }).catch(() => {
          return message.channel.send('an error occured')         
        })
      })
    }

    const muterole1 = message.guild.roles.cache.find(role => role.name === 'muted');

    if (user.roles.cache.has(muterole1?.id)) return message.channel.send('user is already muted')

    user.roles.add(muterole1?.id, reason).then(() => {
      return message.channel.send(`**${user.user.tag}** has been muted 👍`)
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}