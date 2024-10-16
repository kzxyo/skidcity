const jokee = require('discord-jokes')

module.exports = {
  name: "dadjoke",
  description: `sends a random dad joke`,
  usage: '{guildprefix}dadjoke',
  run: async(client, message, args) => {

    jokee.getRandomDadJoke((joke) => {
      return message.channel.send({ content: joke })
    })
  }
}