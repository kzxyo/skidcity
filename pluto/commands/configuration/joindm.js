const { Permissions } = require("discord.js");

module.exports = {
  name: "joindm",
  aliases: ['welcdm', 'welcomedm'],
  description: `dms members on join`,
  subcommands: 'coming soon',
  usage: '{guildprefix}joindm',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    return message.channel.send('disabled till bot is verified')
  }
}