module.exports = {
  name: "kiss",
  aliases: ['mwah', 'mwa', 'ks'],
  description: `give another member a kiss`,
  usage: '{guildprefix}kiss [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) return message.channel.send('you need someone to kiss..')

    message.channel.send(`**${message.author.username}** kisses **${user.user.username}**`)
  }
}