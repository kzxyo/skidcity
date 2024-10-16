module.exports = {
  name: "bite",
  aliases: ['nom'],
  description: `bite a user`,
  usage: '{guildprefix}bite [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) return message.channel.send('you need someone to bite..')

    message.channel.send(`**${message.author.username}** bites **${user.user.username}**`)
  }
}