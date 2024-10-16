const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "8ball",
  aliases: ['8b'],
  description: `ask the magic 8-ball a question`,
  usage: '{guildprefix}8ball [question]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const question = args.join(" ");

    const answers = [
      'no you weak fuck',
      'yes but ur a skid',
      'lmao no but where yo mom at?',
      'nope but add this bot to ur server',
      'no',
      'yes',
      'it is certain',
      `ur mom lol`,
      'outlook not so good',
      'concentrate and ask again',
      'its best not to tell u now',
      'most likely',
      'ask again later dickhead',
      'indeed my good sir',
    ];

    const randomanswers = answers[Math.floor(Math.random() * answers.length)];

    if (!question) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}8ball`)
      .setDescription('ask the magic 8-ball a question')
      .addFields(
      { name: '**usage**', value: `${guildprefix}8ball [question]`, inline: false },
      { name: '**aliases**', value: `8b`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.channel.send(`${message.author}, ${randomanswers}`)
  }
}