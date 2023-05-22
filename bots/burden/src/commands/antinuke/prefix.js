const db = require('../../core/db');

module.exports = {
  name: 'prefix',
  aliases: ['customprefix'],
  run: async (client, message, args) => {
    if (message.member.permissions.has('MANAGE_SERVER')) {

      const newPrefix = args[0];

      if (!newPrefix) {
        message.reply(`provide the prefix you would like to use`);

      } else {
        if (newPrefix.length >= 5) {
          message.reply(`please choose a shorter prefix`)
        } else {
          await db.set(`${message.guild.id}_prefix`, newPrefix);
          message.reply(`:thumbsup:`)
        }
      }
    } else {
      message.reply(`You need **MANAGE_SERVER** permissions to do this`)
    }
  }
}