const { MessageEmbed } = require('discord.js')
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "feedback",
  aliases: ['fb', 'comment', 'suggest'],
  description: `write feedback/suggestions for the bot`,
  usage: 'feedback [comment]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }
  
    const feedbackch = client.channels.cache.get('1018672331033423872')

    const feedback = args.join(" ");

    if (!args[0]) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}feedback`)
      .setDescription('write feedback/suggestions for the bot')
      .addFields(
      { name: '**usage**', value: `${guildprefix}feedback [comment]`, inline: false },
      { name: '**aliases**', value: 'fb, comment, suggest', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle('feedback')
    .setDescription(feedback)
    .setFooter({ text: `sent by ${message.author.tag}` })
    .setTimestamp()

    feedbackch.send({ embeds: [embed] })
  
    message.channel.send('your feedback has been sent 👍')
  }
}