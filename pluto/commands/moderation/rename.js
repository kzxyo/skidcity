const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "rename",
  description: `change a member's nickname`,
  usage: '{guildprefix}rename [user] [nickname]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_NICKNAMES)) return message.channel.send(`this command requires \`manage nicknames\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_NICKNAMES)) return message.channel.send(`this command requires me to have \`manage nicknames\` permission`)

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    if (!user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}rename`)
      .setDescription(`change a member's nickname`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}rename [user] [nickname]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })  
    }

    let nickname = args[1]

    const username = user.user.username

    if (!nickname) nickname = username

    if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`you can't nickname someone above your role`)

    if (user.roles.highest.position >= client.user.roles?.highest.position) return message.channel.send(`i can't nickname someone above my role`)

    let member = message.guild.members.cache.get(user.id)

    await member.setNickname(nickname).then(() => {
      return message.channel.send(`**${user.user.tag}** has been renamed 👍`)
    }).catch(() => {
      return message.channel.send('an error occured')
    })
  }
}