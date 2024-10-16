const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "choose",
  aliases: ['decide', 'pick'],
  description: "pick between options you give",
  usage: '{guildprefix}choose option1 option2',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({
      GuildID: message.guild.id,
    });
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const choice1 = args[0]

    const choice2 = args[1]

    if (!choice1) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}choose`)
      .setDescription('pick between options you give')
      .addFields(
      { name: '**usage**', value: `${guildprefix}choose option1 option2`, inline: false },
      { name: '**aliases**', value: 'decide, pick', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    if (!choice2) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}choose`)
      .setDescription('pick between options you give')
      .addFields(
      { name: '**usage**', value: `${guildprefix}choose option1 option2`, inline: false },
      { name: '**aliases**', value: 'decide, pick', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const answers = [ 
      choice1,
      choice2,
    ];

    const randomanswers = answers[Math.floor(Math.random() * answers.length)];

    message.channel.send(`i think you should choose **${randomanswers}**`)
  }
}