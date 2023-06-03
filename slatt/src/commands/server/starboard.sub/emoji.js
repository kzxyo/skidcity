const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')
module.exports = class Emoji extends Subcommand {
  constructor(client) {
    super(client, {
      base: 'starboard',
      name: 'emoji',
      aliases: ['em'],
      type: client.types.SERVER,
      usage: 'starboard emoji [emoji] or "none"',
      description: 'Update your starboard channel',
    });
  }
  async run(message, args) {
    const db_check = await message.client.db.starboard_emoji.findOne({ where: { guildID: message.guild.id }})
    if (args[0].toLowerCase() === 'none') {
      await message.client.db.starboard_emoji.destroy({ where: { guildID: message.guild.id } })
      return this.send_success(message, `The starboard emoji has been reset to :star:`)
    }
    const Discord = require('discord.js')
    if (!args[0]) return this.invalidArgs(message, `Provide an emoji from this server`)
    const emoji = Discord.Util.parseEmoji(args[0])
    if (!emoji) {
      return this.invalidArgs(message, `Provide a valid emoji from this server`)
    }
    let check = message.guild.emojis.cache.get(emoji.id)
    if (!check && emoji.id) return this.invalidArgs(message, `Provide a valid emoji that is in this server`)
    if (db_check === null) {
      await message.client.db.starboard_emoji.create({
        guildID: message.guild.id,
        emoji: emoji.name,
        emoji_id: emoji.id || null
      })
    } else {
      await message.client.db.starboard_emoji.update({ emoji: emoji.name, emoji_id: emoji.id || null }, { where: { guildID: message.guild.id } })
    }
    return this.send_success(message, `The starboard emoji has been set to ${emoji.id ? `<:${emoji.name}:${emoji.id}>` : `${emoji.name}`}`)
  }
}