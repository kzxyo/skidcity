const db = require('quick.db')
const embedbuilder = require('../utils/embedbuilder/index.js')

module.exports = async (client, member) => {
  let jailrole = await client.db.jail_role.findOne({ where: { guildID: member.guild.id } })
  let jailed = await client.db.jailed.findOne({ where: { userID: member.id, guildID: member.guild.id } })
  if (jailed) {
    const role = member.guild.roles.cache.get(jailrole ? jailrole.role : null) || await member.guild.roles.cache.find(r => r.name.toLowerCase() === 'jailed')
    await member.roles.add(role)
  }
  const muteRoleId = await client.db.mute_role.findOne({ where: { guildID: member.guild.id } })
  const muted = await client.db.muted.findOne({ where: { userID: member.id, guildID: member.guild.id } })
  if (muteRoleId && muted) {
    const role = member.guild.roles.cache.get(muteRoleId ? muteRoleId.role : null)
    await member.roles.add(role)
  }
  let welcomeChannel
  const dbchannel = await client.db.welcome_channel.findOne({ where: { guildID: member.guild.id } })
  if (dbchannel) welcomeChannel = member.guild.channels.cache.get(dbchannel.channel)
  let welcomeMessage = await client.db.welcome_message.findOne({ where: { guildID: member.guild.id } })
  const welcEmbed = await client.db.welcome_message.findOne({ where: { guildID: member.guild.id } })

  if (
    welcomeChannel &&
    welcomeChannel.viewable &&
    welcomeChannel.permissionsFor(member.guild.me).has(['SEND_MESSAGES', 'EMBED_LINKS']) &&
    welcomeMessage
  ) {
    welcomeMessage = client.utils.replace_all_variables(welcomeMessage.message, member, member)
    if (welcomeChannel) welcomeChannel.send(welcomeMessage);
  }
  if (welcEmbed && welcomeMessage === null) {
    const {
      msg,
      embed,
      errors
    } = embedbuilder(client.utils.replace_all_variables(welcEmbed.code, member, member))
    if (welcomeChannel) welcomeChannel.send({
      content: client.utils.replace_all_variables(msg, member, member),
      embeds: [embed]
    })
    if (errors.length > 0) {
      console.log(errors)
    }
  }
  const check = await client.db.autorole.findOne({ where: { guildID: member.guild.id } })
  if (check !== null) {
    const role = member.guild.roles.cache.get(check.role)
    if(role) await member.roles.add(role)
  }
};