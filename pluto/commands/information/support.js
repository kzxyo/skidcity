const { support } = require('./../../config.json')

module.exports = {
  name: "support",
  description: `gets bot support`,
  usage: '{guildprefix}support',
  run: async(client, message, args) => {
  
    message.channel.send(`${message.author}, join this server for any help or questions — ${support}`)
  }
}