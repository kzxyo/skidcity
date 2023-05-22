module.exports = {
  name: "status",

  run: async (client, message, args) => {

    if (message.author.id !== '262429076763967488') return;

    let status = args.join(" ")
    if (!status) return message.channel.send('You need to input **status**')
    client.user.setPresence({
      activity: {
        name: status,
        type: 0,
      }
    })
      .then(message.channel.send(`Set the bot status to **${status}**`))
      .catch(err => {
        return message.channel.send(`There was an error (${err})`)
      })
  }
}
