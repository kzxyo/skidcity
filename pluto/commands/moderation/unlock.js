const { Permissions } = require("discord.js");

module.exports = {
  name: "unlock",
  aliases: ['unlockdown'],
  description: 'unlocks down selected channel',
  usage: 'unlockdown #channel',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) return message.channel.send(`this command requires \`manage channels\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) return message.channel.send(`this command requires me to have \`manage channels\` permission`)

    const lockchannel = message.channel;

    if (lockchannel.permissionsFor(message.guild.id).has('SEND_MESSAGES') === true) {
      return message.channel.send(`**#${lockchannel.name}** is already unlocked`)
    }

    message.guild.roles.cache.forEach(role => {
      lockchannel.permissionOverwrites.edit(role, {
        SEND_MESSAGES: true,
        ADD_REACTIONS: true,
      }).catch(() => { return; })
    })

    message.channel.send(`**#${lockchannel.name}** has been unlocked down 👍`)
  }
}