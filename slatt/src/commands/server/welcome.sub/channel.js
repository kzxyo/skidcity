const Subcommand = require('../../Subcommand.js');
const { MessageEmbed, Guild } = require('discord.js')
const db = require('quick.db')

module.exports = class Message extends Subcommand {
  constructor(client) {
    super(client, {
      base: 'welcome',
      name: 'channel',
      aliases: ['setchannel'],
      type: client.types.SERVER,
      usage: 'welcome channel [channel] or "none"',
      description: 'Update your servers welcome channel',
    });
  }
  async run(message, args) {
    const check = await message.client.db.welcome_channel.findOne({ where: { guildID: message.guild.id } })
    if (args[0].toLowerCase() === 'none') {
      const channel = await message.client.db.welcome_channel.findOne({ where: { guildID: message.guild.id } })
      if (channel === null) {
        return this.send_error(message, 1, `There is no **welcome channel** for this server`)
      } else {
        await message.client.db.welcome_channel.destroy({ where: { guildID: message.guild.id } })
        return this.send_success(message, `The **welcome channel** has been removed`)
      }
    }
    const channel = this.functions.get_channel(message, args.join(' '))
    if (!channel) return this.invalidArgs(message, `There was no channel found named **${args.join(' ')}**`)
    if (check === null) {
      await message.client.db.welcome_channel.create({
        guildID: message.guild.id,
        channel: channel.id
      })
    } else {
      await message.client.db.welcome_channel.update({ channel: channel.id }, { where: { guildID: message.guild.id } })
    }
    return this.send_success(message, `Welcome channel updated to ${channel}`)
  }
}