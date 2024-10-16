const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "uwuify",
  description: `make text uwu - why did i write this command`,
  usage: '{guildprefix}uwuify [text]\n{guildprefix}uwuify hello',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const uwuifytext = args.join(' uwu ');

    if (!uwuifytext) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}uwuify`)
      .setDescription('make text uwu - why did i do this')
      .addFields(
      { name: '**usage**', value: `${guildprefix}uwuify [text]\n${guildprefix}uwuify hello`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.channel.send({ content: uwuifytext })
  }
}