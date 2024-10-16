module.exports = {
  name: "tuck",
  description: `tuck a user into bed`,
  usage: '{guildprefix}tuck [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!user) return message.channel.send(`**${message.author.username}** tucked themself in!.. loser..`)

    message.channel.send(`**${message.author.username}** has tucked **${user.user.username}** in!`)
  }
}