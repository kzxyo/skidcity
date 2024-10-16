module.exports = {
  name: "nuke",
  description:'deletes channel and remakes a new one',
  usage: '{guildprefix}nuke #channel',
  run: async(client, message, args) => {

    if (message.author.id !== message.guild.ownerId) return message.channel.send(`this command is only available to the guild owner`)

    message.channel.clone().then((ch) => {

      ch.setParent(message.channel.parent.id)
      ch.setPosition(message.channel.position)
      message.channel.delete().catch(() => {
        return message.channel.send(`an error occured`)
      })
    
      ch.send('the channel has been nuked 💥')
    }).catch(() => {
      return message.channel.send(`an error occured`)
    })
  }
}