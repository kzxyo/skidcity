const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "imute",
  aliases: ['imgmute', 'imagemute'],
  description: `revoke someone's attachment/embed perms`,
  usage: '{guildprefix}imute [user]\n{guildprefix}imute [user] [reason]',
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

    const muterole = message.guild.roles.cache.find(role => role.name === 'imuted');

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}imute`)
      .setDescription(`revoke someone's attachment/embed perms`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}imute [user]\n${guildprefix}imute [user] [reason]`, inline: false },
      { name: '**aliases**', value: `imgmute, imagemute`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if(user === message.member) return message.channel.send(`you can't imute yourself`) 

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`you can't imute someone above you`)

    if(!muterole) { 
      
      const muterole = await message.guild.roles.create({
        name: 'imuted',
        color: 'DEFAULT',
      }).then(() => {
        return message.channel.send('setting up imute for the first time..')
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

    const muterole1 = message.guild.roles.cache.find(role => role.name === 'imuted');

    if (user.roles.cache.has(muterole1?.id)) return message.channel.send('user is already imuted')

    user.roles.add(muterole1.id, reason).then(() => {
      return message.channel.send(`**${user.user.tag}** has been image muted 👍`)
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}