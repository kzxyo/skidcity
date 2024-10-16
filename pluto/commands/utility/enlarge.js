const { MessageEmbed, Util } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "enlarge",
  aliases: ['e'],
  description: 'enlarge an emoji',
  usage: '{guildprefix}enlarge [emoji]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const emoji = args[0];

    if (!emoji) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}enlarge`)
      .setDescription('enlarge an emoji')
      .addFields(
      { name: '**usage**', value: `${guildprefix}enlarge [emoji]`, inline: false },
      { name: '**aliases**', value: 'e', inline: false },
      )
      return message.channel.send({ embeds: [embed] })
    }

    let custom = Util.parseEmoji(emoji);

    const embed = new MessageEmbed()

    .setColor(embedcolor)

    if (custom.id) {
      embed.setImage(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`);
      return message.channel.send({ embeds: [embed] })
    } else {
      return message.channel.send(`i couldn't find any emoji to enlarge`)
    }
  }
}