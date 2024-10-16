const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "sendembed",
  aliases: ['se'],
  description: "send an embed using JSON",
  usage: '{guildprefix}sendembed [json]\n{guildprefix}sendembed {"title": "embed", "description": "this is an embed"}',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires me to have \`manage messages\` permission`)

    if (!args[0]) {
      
      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}sendembed`)
      .setDescription('send an embed using JSON')
      .addFields(
      { name: '**usage**', value: `${guildprefix}sendembed [json]\n${guildprefix}sendembed {"content": "welcome to", "title": "embed", "description": "this is an embed"}`, inline: false },
      { name: '**aliases**', value: `se`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    try {

      const json = JSON.parse(args.join(' '))
      const { content = '' } = json

      if ({}.hasOwnProperty.call(json, "thumbnail")) {
        json.thumbnail = { url: json.thumbnail };
      }
      
      if ({}.hasOwnProperty.call(json, "image")) {
        json.image = { url: json.image };
      }

      return message.channel.send({ content: content, embeds: [json] }).catch(() => {
        return message.channel.send('an error occured')
      })
    } catch (e) {
      message.channel.send('an error occured');
    }
  }
}