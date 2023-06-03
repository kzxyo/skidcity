
const db = require("quick.db")
module.exports = async (client, oldMember, newMember) => {
  const boost_channel = await client.db.boost_channel.findOne({ where: { guildID: newMember.guild.id } })
  const boost_message = await client.db.boost_message.findOne({ where: { guildID: newMember.guild.id } })
  if (!oldMember.premiumSince && newMember.premiumSince) {
    if (boost_channel && boost_message) {
      client.logger.info(`${newMember.user.tag} just boosted guild ${newMember.guild.name}`)
      const channel = newMember.guild.channels.cache.get(boost_channel.channel)
      channel.send(boost_message.message
        .replace(`{user.mention}`, newMember)
        .replace(`{user.tag}`, newMember.user.tag)
        .replace(`{user.username}`, newMember.user.username)
        .replace(`{server.boosts}`, newMember.guild.premiumSubscriptionCount)
        .replace(`{guild.name}`, newMember.guild.name)
      )
    }
  }
}