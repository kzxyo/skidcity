const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "rmute",
  aliases: ['reactmute', 'reactionmute', 'emojimute', 'emotemute', 'emute'],
  description: `revoke someone's reaction/emote perms`,
  usage: '{guildprefix}rmute [user]\n{guildprefix}rmute [user] [reason]',
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
      .setTitle(`${guildprefix}rmute`)
      .setDescription(`revoke someone's reaction/emote perms`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}rmute [user]\n${guildprefix}rmute [user] [reason]`, inline: false },
      { name: '**aliases**', value: `reactmute, reactionmute, emojimute, emotemute, emute`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if(user === message.member) return message.channel.send(`you can't rmute yourself`) 

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`you can't rmute someone above you`)

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
          USE_EXTERNAL_EMOJIS: false,
          ADD_REACTIONS: false,
        }).catch(() => {
          return message.channel.send('an error occured')         
        })
      })
    }

    const muterole1 = message.guild.roles.cache.find(role => role.name === 'rmuted');

    if (user.roles.cache.has(muterole1?.id)) return message.channel.send('user is already rmuted')

    user.roles.add(muterole1.id, reason).then(() => {
      return message.channel.send(`**${user.user.tag}** has been rmuted 👍`)
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}