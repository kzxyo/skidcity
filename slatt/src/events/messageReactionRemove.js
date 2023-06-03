const {
    MessageEmbed
} = require('discord.js');
const db = require('quick.db')
const moment = require('moment');
module.exports = async (client, messageReaction, user) => {
    const {
        message,
        emoji
    } = messageReaction
    const starboardChannelId = await client.db.starboard.findOne({ where: { guildID: message.guild.id } })
    const channel = message.guild.channels.cache.get(starboardChannelId ? starboardChannelId.channel : null)
    const starEmoji = await client.db.starboard_emoji.findOne({ where: { guildID: message.guild.id } })
    if(!channel) return
    const starred = db.get(`Starred_${message.guild.id}`)
    if (starred && starred.message === message.id) {
        const StarredMessage = await channel.messages.fetch(starred.starred)
        if(!message.reactions.cache.first()) return StarredMessage.edit({content: `${StarredMessage.content.split(' |')[0]} | #0`, embeds: [StarredMessage.embeds[0]]})
        StarredMessage.edit({content: `${StarredMessage.content.split(' |')[0]} | ${message.reactions.cache.filter(x => x._emoji.name === '⭐' || x._emoji.id === starEmoji.emoji_id)[0] ? `#${message.reactions.cache.filter(x => x._emoji.name === '⭐' || x._emoji.id === starEmoji.emoji_id)[0].count}` : '#0'}`,embeds: [StarredMessage.embeds[0]]})
    }
}