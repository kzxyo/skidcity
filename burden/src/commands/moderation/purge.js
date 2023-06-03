module.exports = {
  name: 'purge',
  aliases: ['clear', 'c'],
  run: async (client, message, args) => {
    if (!message.member.permissions.has('MANAGE_MESSAGES')) {
      message.reply(`you do not have permission to **MANAGE_MESSAGES**`)
    } else {
      const amount = args[0];
      if (!amount) {
        message.reply('please provide a number of messages')
      } else {
        if (!parseInt(amount)) {
          message.reply('provide a number uner __100__ to purge')
        } else if (amount >= 101) {
          message.reply('enter a number below 100')
        } else {
          await message.channel.messages.fetch({ limit: parseInt(amount) }).then(msgs => {
            msgs.forEach(msg => {
              msg.delete();
            })
          })
          message.channel.send(`:thumbsup:`)
        }
      }
    }
  }
}