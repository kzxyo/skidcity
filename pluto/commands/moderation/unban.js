const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "unban",
  description: `unban a user from the server`,
  usage: '{guildprefix}unban [user]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires \`ban members\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires me to have \`ban members\` permission`)

    const banneduseraudit = await message.guild.bans.fetch()

    const user = banneduseraudit.get(args[0])

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}unban`)
      .setDescription('unban a user from the server')
      .addFields(
      { name: '**usage**', value: `${guildprefix}unban [user]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.guild.members.unban(user.user.id).then(() => {
      return message.channel.send(`**${user.user.tag}** has been unbanned 👍`)
    }).catch(() => {
      return message.channel.send('an error occured')
    })
  }
}