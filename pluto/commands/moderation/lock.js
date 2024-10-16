const { Permissions } = require("discord.js");

module.exports = {
  name: "lock",
  aliases: ['lockdown'],
  description: 'locks down selected channel',
  usage: '{guildprefix}lockdown #channel',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) return message.channel.send(`this command requires \`manage channels\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) return message.channel.send(`this command requires me to have \`manage channels\` permission`)

    const lockchannel = message.channel;

    if (lockchannel.permissionsFor(message.guild.id).has('SEND_MESSAGES') === false) {
      return message.channel.send(`**#${lockchannel.name}** is already locked`)
    }

    message.guild.roles.cache.forEach(role => {
      lockchannel.permissionOverwrites.edit(role, {
        SEND_MESSAGES: false,
        ADD_REACTIONS: false,
      }).catch(() => { return; })
    })

    message.channel.send(`**#${lockchannel.name}** has been locked down 👍`)
  }
}