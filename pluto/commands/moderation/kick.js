const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "kick",
  aliases: ['k', 'kick', 'boot',],
  description: 'kick a user from the server',
  usage: '{guildprefix}kick [user]\n{guildprefix}kick [user] [reason]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return message.channel.send(`this command requires \`kick members\` permission`)

  if(!message.guild.me.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return message.channel.send(`this command requires me to have \`kick members\` permission`)

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}kick`)
      .setDescription('kick a user from the server')
      .addFields(
      { name: '**usage**', value: `${guildprefix}kick [user]\n${guildprefix}kick [user] [reason]`, inline: false },
      { name: '**aliases**', value: `k, kick, boot`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    let reason = args.slice(1).join(" ");

    if (!reason) reason = 'n/a'

    if(user === message.member) return message.channel.send(`kick yourself.. loser..`)

    if (!user.kickable) return message.channel.send(`i can't kick someone above my top role`)

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send('you cant kick someone above your role')

    user.kick({ reason: `${reason}` }).then(() => {
      return message.channel.send(`**${user.user.tag}** has been kicked 👍`)
    }).catch(() => {
      return message.channel.send('an error occured')
    })
  }
}