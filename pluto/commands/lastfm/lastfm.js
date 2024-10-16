const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const lastfmuserschema = require('../../database/lastfm')

module.exports = {
  name: "lastfm",
  aliases: ['lf'],
  description: 'all commands that interact with the last.fm website',
  subcommands: '{guildprefix}lastfm howto - how to use/setup last.fm with pluto\n{guildprefix}lastfm set - link a last.fm profile to your discord\n{guildprefix}lastfm unlink - unlink your last.fm data from pluto',
  usage: '{guildprefix}lastfm',
  run: async(client, message, args) => {
  
    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const fmdata = await lastfmuserschema.findOne({ UserID: message.author.id })
    
    if (args[0] === 'howto') {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .addFields(
      { name: '**step 1**', value: `register here: [last.fm/join](https://www.last.fm/join)`, inline: false },
      { name: '**step 2**', value: `• for spotify users: [click here](https://www.last.fm/settings/applications)\n• for other music services: [click here](https://www.last.fm/about/trackmymusic)`, inline: false },
      { name: '**step 3**', value: `\`\`\`${guildprefix}lf set your_lastfm_username\`\`\``, inline: false },
      { name: '**step 4**', value: `listen to music and wait for it to show up — **sometimes it takes a few minutes**`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })

    } else if (args[0] === 'set') {

      const fmuser = args[1]

      if (!fmuser) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)         
        .setTitle(`${guildprefix}lastfm`)
        .setDescription(`link a last.fm profile to your discord`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}lastfm set [username]`, inline: false },
        )
      
        return message.channel.send({ embeds: [embed] })
      }

      if (fmdata) {
      
        await lastfmuserschema.findOneAndRemove({ UserID: message.author.id });

        let newdata = new lastfmuserschema({ UserID: message.author.id, Username: fmuser });
      
        newdata.save();     
      
        return message.channel.send(`your last.fm profile has been set to **${fmuser}** 👍`)

      } else if (!fmdata) {

        let newdata = new lastfmuserschema({ UserID: message.author.id, Username: fmuser });
      
        newdata.save();

        return message.channel.send(`your last.fm profile has been set to **${fmuser}** 👍`)
      }

    } else if (args[0] === 'unlink') {

      const fmdata = new lastfmuserschema({ UserID: message.author.id, Username: fmuser });

      if (fmdata) {

        await lastfmuserschema.findOneAndRemove({ UserID: message.author.id });

        return message.channel.send(`your last.fm profile has been reset 👍`)

      } else {
        
        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`you don't have a last.fm linked, use \`${guildprefix}lastfm set [username]\``)

        return message.channel.send({ embeds: [embed] })
      }
      
    } else {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}lastfm`)
      .setDescription(`all commands that interact with the last.fm website`)
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}lastfm howto - how to use/setup last.fm with pluto\n${guildprefix}lastfm set - link a last.fm profile to your discord\n${guildprefix}lastfm unlink - unlink your last.fm data from pluto`, inline: false },
      { name: '**usage**', value: `${guildprefix}lastfm`, inline: false },
      { name: '**aliases**', value: `lf`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })    
    }   
  }
}