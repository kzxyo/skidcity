const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "setbanner",
  description: "sets the guild banner",
  usage: '{guildprefix}setbanner [url]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires \`manage server\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires me to have \`manage server\` permission`)

    let banner = args[0]

    if (!message.guild.features.includes("BANNER")) return message.channel.send('this command requires guild level 2')

    if (!banner) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}setbanner`)
      .setDescription('sets the guild banner')
      .addFields(
      { name: '**usage**', value: `${guildprefix}setbanner [url]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.guild.setBanner(banner).then(() => {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`set the guild banner to [this image](${banner})`)

      return message.channel.send({ embeds: [embed] })
    }).catch(() => { 
      return message.channel.send(`an error occured`)
    })
  }
}