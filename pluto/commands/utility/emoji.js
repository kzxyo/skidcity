const { MessageEmbed, Permissions, Util } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const moment = require('moment')

module.exports = {
  name: "emoji",
  aliases: ['em', 'emote'],
  description: 'manage server emojis',
  subcommands: `{guildprefix}emoji add - add an emoji to the server via emoji/file/url\n{guildprefix}emoji info - display an emoji's information\n{guildprefix}emoji remove - remove an emoji from the server\n{guildprefix}emoji rename - rename a server emoji`,
  usage: '{guildprefix}emoji add [emoji]\n{guildprefix}emoji remove [emoji]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_EMOJIS_AND_STICKERS)) return message.channel.send(`this command requires \`manage emojis\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_EMOJIS_AND_STICKERS)) return message.channel.send(`this command requires me to have \`manage emojis\` permission`)

    if (args[0] === 'add') {

      const emoji = args[1]

      if (!emoji) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}emoji add`)
        .setDescription(`add an emoji`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}emoji add [emoji]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

    let parsedemoji = Util.parseEmoji(emoji)

    if (parsedemoji.id) {

      const emojiext = parsedemoji.animated ? ".gif" : ".png";
      
      const emojiurl = `https://cdn.discordapp.com/emojis/${parsedemoji.id + emojiext}`

      message.guild.emojis.create(emojiurl, parsedemoji.name).then((em) => { 

        return message.channel.send(`added the emoji \`${em.name}\` ${em.toString()} 👍`)
      
      }).catch(() => {
        return message.channel.send('an error occured')
      })
    
    } else {
      return message.channel.send('provide a custom emoji')
    }

    } else if (args[0] === 'info') {

      const emoji = args[1]

      if (!emoji) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}emoji info`)
        .setDescription(`display an emoji's information`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}emoji info [emoji]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      let parsedemoji = Util.parseEmoji(emoji)

      const emojiinfo = message.guild.emojis.cache.get(parsedemoji.id);

      if (!emojiinfo) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`unable to find an emoji`)

        return message.channel.send({ embeds: [embed] })
      }

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${emojiinfo.name} ${emojiinfo.toString()}`)
      .setDescription(`name: ${emojiinfo.name}\nid: \`${emojiinfo.id}\`\ncreated: ${moment(emojiinfo.createdAt).format("MM/DD/YYYY")}`)
      .setThumbnail(emojiinfo.url)

      return message.channel.send({ embeds: [embed] })

    } else if (args[0] === 'remove') {

      const emoji = args[1]

      let parsedemoji = Util.parseEmoji(emoji)

      const emojiinfo = message.guild.emojis.cache.get(parsedemoji.id);

      if (!emojiinfo) return message.channel.send('give me an emoji to delete')

      emojiinfo.delete().then(() => {
        return message.channel.send(`deleted the emoji \`:${emojiinfo.name}:\` 👍`)
      }).catch(() => {
        return message.channel.send('an error occured')
      })

    } else if (args[0] === 'rename') {

      const emoji = args[1]

      let name = args.slice(2).join(" ");

      if (!emoji) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}emoji rename`)
        .setDescription(`rename a server emoji`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}emoji rename [emoji] [name]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (!name) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}emoji rename`)
        .setDescription(`rename a server emoji`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}emoji rename [emoji] [name]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      let parsedemoji = Util.parseEmoji(emoji)

      const emojiinfo = message.guild.emojis.cache.get(parsedemoji.id);

      if (!emojiinfo) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`unable to find an emoji`)

        return message.channel.send({ embeds: [embed] })
      }
    
      emojiinfo.setName(name).then(() => {
        return message.channel.send(`renamed the emoji\`:${emojiinfo.name}:\` to \`:${name}:\` 👍`)
      }).catch(() => {
        return message.channel.send('an error occured') 
      })

    } else {
      
      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}emoji`)
      .setDescription('manage server emojis')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}emoji add - add an emoji to the server via emoji/file/url\n${guildprefix}emoji info - display an emoji's information\n${guildprefix}emoji remove - remove an emoji from the server\n${guildprefix}emoji rename - rename a server emoji`, inline: false },
      { name: '**usage**', value: `${guildprefix}emoji add [emoji]\n${guildprefix}emoji remove [emoji]`, inline: false },
      { name: '**aliases**', value: 'em, emote', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }
  }
}