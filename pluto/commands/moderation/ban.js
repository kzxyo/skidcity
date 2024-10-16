const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "ban",
  aliases: ['b', 'deport', 'yeet'],
  description: 'ban a user from the server',
  usage: '{guildprefix}ban [user]\n{guildprefix}ban [user] [reason]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires \`ban members\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires me to have \`ban members\` permission`)

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    if (!user) {

      const embed = new MessageEmbed()
  
      .setColor(embedcolor)
      .setTitle(`${guildprefix}ban`)
      .setDescription('ban a user from the server')
      .addFields(
      { name: '**usage**', value: `${guildprefix}ban [user]\n${guildprefix}ban [user] [reason]`, inline: false },
      { name: '**aliases**', value: `b, deport, yeet`, inline: false },
      )
  
      return message.channel.send({ embeds: [embed] })
    }

    let reason = args.slice(1).join(" ");

    if (!reason) reason = 'n/a'

    if(user === message.member) return message.channel.send(`ban yourself.. loser..`)

    if (!user.bannable) return message.channel.send(`i can't ban someone above my top role`)

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send('you cant ban someone above your role')

    user.ban({ reason: `${reason}` }).then(() => {
      return message.channel.send(`**${user.user.tag}** has been banned 👍`)
    }).catch(() => {
      return message.channel.send('an error occured')
    })
  }
}