const {
  MessageEmbed
} = require('discord.js');
const db = require('quick.db')
const moment = require('moment');
const Discord = require('discord.js')
module.exports = async (client, messageReaction, user) => {
  const {
    message,
    emoji
  } = messageReaction
  if (client.user === user) return;
  const starboardChannelId = await client.db.starboard.findOne({ where: { guildID: message.guild.id } })
  const channel = message.guild.channels.cache.get(starboardChannelId ? starboardChannelId.channel : null)
  const starEmoji = await client.db.starboard_emoji.findOne({ where: { guildID: message.guild.id } })
  let count
  const threshold = db.get(`starboard_threshold_${message.guild.id}`)
  if (threshold) {
    count = parseInt(threshold)
  } else {
    count = 1
  }
  if (starEmoji && emoji) {
    if (emoji.id && emoji.id === starEmoji.emoji_id) {
      let av = `https://cdn.discordapp.com/avatars/${message.author.id}/${message.author.avatar}.webp?size=512`
      if (message.embeds.length) {
        const embed = new MessageEmbed(message.embeds[0])
        embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
        if (!embed.footer) embed.setFooter(message.channel.id)
        if (!embed.timestamp) embed.setTimestamp()
        if (channel && Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count === count) {
          channel.send({ content: `${emoji} | #${count}`, embeds: [embed] }).then(msg => {
            db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
          })
        } else {
          const starred = db.get(`Starred_${message.guild.id}`)
          if (starred && starred.message === message.id) {
            const StarredMessage = await channel.messages.fetch(starred.starred)
            StarredMessage.edit({
              content: `${emoji} | #${Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count}`,
              embeds: [StarredMessage.embeds[0]]
            })
          }
        }
      } else {
        const embed = new MessageEmbed()
          .setAuthor(message.author.username + '#' + message.author.discriminator, av)
          .setColor(`#303135`)
          .setDescription(message.content)
        if (message.attachments.first()) embed.addField(`Attachment: ${message.attachments.first().name}`, `[${message.attachments.first().name}](${message.attachments.first().url})`)
        embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
        embed.setFooter(message.channel.id)
        embed.setTimestamp()
        if (message.attachments.first()) embed.setImage(message.attachments.first().url)
        if (channel && Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count === count) {
          channel.send({ content: `${emoji} | #${count}`, embeds: [embed] }).then(msg => {
            db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
          })
        } else {
          const starred = db.get(`Starred_${message.guild.id}`)
          if (starred && starred.message === message.id) {
            const StarredMessage = await channel.messages.fetch(starred.starred)
            StarredMessage.edit({
              content: `${emoji} | #${Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count}`,
              embeds: [StarredMessage.embeds[0]]
            })
          }
        }
      }
    } else if (starEmoji && emoji.id && starEmoji.emoji_id === emoji.id) {
      const embed = new MessageEmbed()
        .setAuthor(message.author.username + '#' + message.author.discriminator, av)
        .setColor(`#303135`)
        .setDescription(message.content)
      if (message.attachments) embed.addField(`Attachment: ${message.attachments.first().name}`, `[${message.attachments.first().name}](${message.attachments.first().url})`)
      embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
      embed.setFooter(message.channel.id)
      embed.setTimestamp()
      if (message.attachments.first()) embed.setImage(message.attachments.first().url)
      if (channel && Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count === count) {
        channel.send({ content: `<:${starEmoji.emoji}:${starEmoji.emoji_id}> | #${count}`, embeds: [embed] }).then(msg => {
          db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
        })
      } else {
        const starred = db.get(`Starred_${message.guild.id}`)
        if (starred && starred.message === message.id) {
          const StarredMessage = await channel.messages.fetch(starred.starred)
          StarredMessage.edit(`<:${starEmoji.emoji}:${starEmoji.emoji_id}> | #${Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count}`, StarredMessage.embeds[0])
        }
      }
    } else if (!starEmoji && emoji.name === '⭐') {
      let av = `https://cdn.discordapp.com/avatars/${message.author.id}/${message.author.avatar}.webp?size=512`
      const embed = new MessageEmbed()
        .setAuthor(message.author.username + '#' + message.author.discriminator, av)
        .setColor(`#303135`)
        .setDescription(message.content)
      if (message.attachments) embed.addField(`Attachment: ${message.attachments.first().name}`, `[${message.attachments.first().name}](${message.attachments.first().url})`)
      embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
      embed.setFooter(message.channel.id)
      embed.setTimestamp()
      if (message.attachments.first()) embed.setImage(message.attachments.first().url)
      if (channel && emoji.count === count) {
        channel.send({ content: `:star: | #${count}`, embeds: [embed] }).then(msg => {
          db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
        })
      } else {
        const starred = db.get(`Starred_${message.guild.id}`)
        if (starred && starred.message === message.id) {
          const StarredMessage = await channel.messages.fetch(starred.starred)
          StarredMessage.edit({
            content: `:star: | #${Array(message.reactions.cache.first()).filter(x => x._emoji.name === '⭐')[0].count}`,
            embeds: [StarredMessage.embeds[0]]
          })
        }
      }
    } else if (!emoji.id && emoji.name === starEmoji.emoji) {
      let av = `https://cdn.discordapp.com/avatars/${message.author.id}/${message.author.avatar}.webp?size=512`
      if (message.embeds.length) {
        const embed = new MessageEmbed(message.embeds[0])
        embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
        if (!embed.footer) embed.setFooter(message.channel.id)
        if (!embed.timestamp) embed.setTimestamp()
        if (channel && Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count === count) {
          channel.send({ content: `${emoji} | #${count}`, embeds: [embed] }).then(msg => {
            db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
          })
        } else {
          const starred = db.get(`Starred_${message.guild.id}`)
          if (starred && starred.message === message.id) {
            const StarredMessage = await channel.messages.fetch(starred.starred)
            StarredMessage.edit({
              content: `${emoji} | #${Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count}`,
              embeds: [StarredMessage.embeds[0]]
            })
          }
        }
      } else {
        const embed = new MessageEmbed()
          .setAuthor(message.author.username + '#' + message.author.discriminator, av)
          .setColor(`#303135`)
          .setDescription(message.content)
        if (message.attachments.first()) embed.addField(`Attachment: ${message.attachments.first().name}`, `[${message.attachments.first().name}](${message.attachments.first().url})`)
        embed.addField(`Message`, `[Jump](https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id})`)
        embed.setFooter(message.channel.id)
        embed.setTimestamp()
        if (message.attachments.first()) embed.setImage(message.attachments.first().url)
        if (channel && Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count === count) {
          channel.send({ content: `${emoji} | #${count}`, embeds: [embed] }).then(msg => {
            db.set(`Starred_${message.guild.id}`, { starred: msg.id, message: message.id })
          })
        } else {
          const starred = db.get(`Starred_${message.guild.id}`)
          if (starred && starred.message === message.id) {
            const StarredMessage = await channel.messages.fetch(starred.starred)
            StarredMessage.edit({
              content: `${emoji} | #${Array(message.reactions.cache.first()).filter(x => x._emoji.id === starEmoji.emoji_id)[0].count}`,
              embeds: [StarredMessage.embeds[0]]
            })
          }
        }
      }
    }
  }
}