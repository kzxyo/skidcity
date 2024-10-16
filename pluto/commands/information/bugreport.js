const { MessageEmbed } = require('discord.js')
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "bugreport",
  aliases: ['reportbug', 'bug', 'report', 'issue', 'complaint'],
  description: `report bugs/issues with the bot`,
  usage: '{guildprefix}bugreport [comment]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }
  
    const bugreport = args.join(" ");

    if (!args[0]) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}bugreport`)
      .setDescription('report bugs/issues with the bot')
      .addFields(
      { name: '**usage**', value: `${guildprefix}bugreport [comment]`, inline: false },
      { name: '**aliases**', value: 'reportbug, bug, report, issue, complaint', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const bugreportchannel = client.channels.cache.get('11288462423505895445')

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle('bug report')
    .setDescription(bugreport)
    .setFooter({ text: `sent by ${message.author.tag}` })
    .setTimestamp()

    bugreportchannel.send({ embeds: [embed] })
  
    message.channel.send('your bug report has been sent 👍')
  }
}