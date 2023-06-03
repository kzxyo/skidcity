module.exports = {
  name: "leave",
  category: "owner",

  run: async (client, message, args) => {
    if (message.author.id === '262429076763967488') {
      client.guilds.fetch(args[0]).then(guild => guild.leave().catch(console.error).then(message.channel.send({ embed: { color: "#a3eb7b", description: `<:approve:853434679738105897> ${message.author}: Successfully left **${guild.name}**` } })))
    }
  }
}