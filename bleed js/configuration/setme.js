const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "setme",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_ROLES", "MANAGE_CHANNELS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_channels or manage_roles\`` } });

    message.channel.send({ embed: { color: "#6495ED", description: `:gear: ${message.author}: Working moderation setup...` } }).then(embedMessage => {
      embedMessage.edit({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: **Moderation system set** up has been completed. Please make sure that all of your channels and roles have been configured properly.` } })
    })

    message.guild.roles.create({
      data: {
        name: 'muted',
        permissions: []
      }
    });
    message.guild.roles.create({
      data: {
        name: 'jailed',
        permissions: []
      }
    });
    message.guild.channels.create("jailed", {
      type: "text",
      position: 0,
      permissions: ['VIEW_CHANNEL']
    })
  }
}