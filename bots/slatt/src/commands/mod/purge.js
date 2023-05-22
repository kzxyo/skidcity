const Command = require('../Command.js');


module.exports = class PurgeCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'purge',
      aliases: ['clear', 'p', 'prune'],
      type: client.types.MOD,
      usage: `purge [member] [number]`,
      description: 'purge messages in your channel',
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_MESSAGES'],
      userPermissions: ['MANAGE_MESSAGES'],
    });
  }
  async run(message, args) {
    if (message.client.subcommands.get(`purge ${args[0]}`) || message.client.subcommand_aliases.get(`purge ${args[0]}`)) return
    let member = this.functions.get_member(message, args[0])
    let amount
    if (!member || parseInt(args[0])) {
      member = null; amount = args[0];
    } else {
      amount = args[1]
    }
    if(!parseInt(amount) || parseInt(amount) && parseInt(amount) > 100) return this.send_error(message, 1, `Provide a number between 1 and 100 to purge ${member ? `from **${member.user.tag}**` : ''}`)
    let messages;
    if (member) {
      messages = (await message.channel.messages.fetch({
        limit: amount
      })).filter(m => m.member.id === member.id);
    } else messages = amount;
    if (messages.size === 0) {
      return this.send_error(message, 1, `I could not find any messages from ${member}`)
    } else {
      message.channel.bulkDelete(messages, true)
      message.client.utils.send_log_message(message, member || message.member, this.name, `**${amount}** messages purged from ${message.channel}`)
    }
    message.delete()
  }
}