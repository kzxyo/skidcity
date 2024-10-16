const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const urban = require('relevant-urban');
const globaldataschema = require('../../database/global')

module.exports = {
  name: "urban",
  aliases: ['ud', 'urban'],
  description: "get a word's definition from urbandictionary",
  usage: '{guildprefix}urban [word]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

     const urbanword = args.join(" ");

    if (!urbanword) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}urbandictionary`)
      .setDescription(`get a word's definition from urbandictionary`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}urban [word]`, inline: false },
      { name: '**aliases**', value: `ud, urban`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    try {

      const word = await urban(`${urbanword}`)

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(word.word)
      .setURL(word.urbanURL)
      .setDescription(word.definition)
      .addFields(
      { name: '**example**', value: `\`\`\`${word.example}\`\`\``, inline: false },
      )

      return message.channel.send({ embeds: [embed] })

    } catch {
      return message.channel.send(`that word isn't on urbandictionary`)
    }
  }
}