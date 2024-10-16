const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const ytsearch = require("yt-search");

module.exports = {
  name: "youtube",
  aliases: ['yt'],
  description: `search for a song/video on youtube`,
  usage: '{guildprefix}youtube [song/video]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const youtubesearch = args.join(' ')  

    if(!youtubesearch) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}youtube`)
      .setDescription(`search for a song/video on youtube`)
      .addFields(
      { name: '**usage**', value: `${guildprefix}youtube [song/video]`, inline: false },
      { name: '**aliases**', value: 'yt', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

     const res = await ytsearch(youtubesearch).catch(() => {
      return message.channel.send('no results found')
     })

    const video = res.videos[0];
      
    if (!video) return message.channel.send('no results found')

    return message.channel.send({ content: `${video.url}` })
  }
}