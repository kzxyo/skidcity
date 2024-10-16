const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "seticon",
  description: "sets the guild icon",
  usage: '{guildprefix}seticon [url]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires \`manage server\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires me to have \`manage server\` permission`)

    let icon = args[0]

    if (!icon) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}seticon`)
      .setDescription('sets the guild icon')
      .addFields(
      { name: '**usage**', value: `${guildprefix}seticon [url]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.guild.setIcon(icon).then(() => {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`set the guild icon to [this image](${icon})`)

      return message.channel.send({ embeds: [embed] })
    }).catch(() => { 
      return message.channel.send(`an error occured`)
    })
  }
}