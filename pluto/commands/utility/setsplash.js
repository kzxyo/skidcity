const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "setsplash",
  description: "sets the guild splash",
  usage: '{guildprefix}setsplash [url]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires \`manage server\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires me to have \`manage server\` permission`)

    let splash = args[0]

    if (!message.guild.features.includes("BANNER")) return message.channel.send('this command requires guild level 1')

    if (!splash) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}setsplash`)
      .setDescription('sets the guild splash')
      .addFields(
      { name: '**usage**', value: `${guildprefix}setsplash [url]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.guild.setSplash(splash).then(() => {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`set the guild splash to [this image](${splash})`)

      return message.channel.send({ embeds: [embed] })
    }).catch(() => { 
      return message.channel.send(`an error occured`)
    })
  }
}