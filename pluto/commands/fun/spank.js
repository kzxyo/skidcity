module.exports = {
  name: "spank",
  description: `spank another member`,
  usage: '{guildprefix}spank [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) return message.channel.send('you need someone to spank..')

    message.channel.send(`**${message.author.username}** spanks **${user.user.username}**`)
  }
}