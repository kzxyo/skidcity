const { MessageEmbed } = require("discord.js")
const { setFilter } = require('distube')

module.exports = {
  configuration: {
    commandName: 'filter',
    aliases: ["filters", "setfilter"],
    description: "Set Music Filter",
    syntax: 'filter [filter]',
    example: 'filter bassboost',
    permissions: 'N/A',
    parameters: 'filter',
    module: "music",
    subcommands: ['> filter bassboost\n> filter nightcore\n> filter echo\n> filter vaporwave\n> filter 3d\n> filter karaoke']
  },
  run: async (session, message, args) => {
    if (!message.member.voice.channel) {
      const filterError = new MessageEmbed()
        .setDescription(`${session.mark} ${message.author}: You must be in a **voice channel**`)
        .setColor(session.warn)
      return message.channel.send({ embeds: [filterError] })
    }
    const queue = session.player.getQueue(message);

    if (!queue) {
      const filterError2 = new MessageEmbed()
        .setDescription(`${session.mark} ${message.author}: There is nothing playing`)
        .setColor(session.warn)
      return message.channel.send({ embeds: [filterError2] })
    }

    let filterOption = args[0];
    if (!args[0]) {
      const filterOptions = new MessageEmbed()
        .setColor(session.color)
        .setTitle(`**Filters**`)
      .setDescription(`**bassboost** - adds extra boost \n**echo** - adds a echo effect \n**nightcore** - adds a nightcore effect \n**vaporwave** - adds a vaporwave effect \n**3d** - adds a 3d effect \n**karaoke** adds a karaoke effect`)

      return message.channel.send({ embeds: [filterOptions] })
    }

    try {
      await session.player.setFilter(message, filterOption)
      const embed = new MessageEmbed()
        .setDescription('Music Filter is on : ' + `**${filterOption}**` || 'Off')
        .setColor(session.color)

      return message.channel.send({ embeds: [embed] })
    } catch (error) {
      return;
    }



  }
}