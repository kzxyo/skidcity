module.exports = {
  name: "hug",
  description: `give another member a hug`,
  usage: '{guildprefix}hug [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) return message.channel.send('you need someone to hug..')

    message.channel.send(`**${message.author.username}** hugs **${user.user.username}**`)
  }
}