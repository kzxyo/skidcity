const Command = require('../Command.js');
const Discord = require('discord.js');

module.exports = class UnLockdownCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'unlock',
      aliases: ['unlockdown'],
      subcommands: ['unlock'],
      description: 'unlocks a channel',
      type: client.types.MOD,
      clientPermissions: ['MANAGE_CHANNELS'],
      userPermissions: ['MANAGE_CHANNELS']
    });

  }

  async run(message, args) {
    let channel = await this.functions.get_channel(message, args.join(' '))
    await channel.permissionOverwrites.create(message.guild.id, {
        SEND_MESSAGES: true,
    })
    message.client.utils.send_log_message(message, message.member, this.name, `${channel} has been unlocked`)
    return this.send_success(message, `i have removed the lockdown for ${channel}`)
  }
}