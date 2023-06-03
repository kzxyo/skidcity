const {
  MessageEmbed
} = require('discord.js');
const db = require('quick.db')

module.exports = async (client, guild) => {
  if(db.get(`BLACKLIST_GUILD_${guild.id}`)) {
    await guild.leave()
    client.logger.info(`Blacklisted guild ${guild.name} (${guild.id}) tried inviting`)
    return 
  }
  if(!await client.db.prefix.findOne({where: {guildID: guild.id}})) await client.db.prefix.create({
    guildID: guild.id,
    prefix: ';'
  })
  client.logger.info(`${guild.name} created with new prefix`)
  let server_log = client.channels.cache.get('898095517706358815')
  const embed = new MessageEmbed()
    .setTitle(`Guild Joined`)
    .setThumbnail(guild.iconURL({
      dynamic: true
    }))
    .addField(`Guild`, guild.name + `\`(${guild.id})\``)
    .addField(`Membercount`, `${guild.memberCount}`)
    .addField(`Owned by`, guild.members.cache.get(guild.ownerId).user.tag)
    .setColor('#303135')
  server_log.send({embeds: [embed]})
  client.logger.info(`slatt has joined ${guild.name} membercount ${guild.memberCount}`);
  let muteRole = guild.roles.cache.find(r => r.name.toLowerCase() === 'muted');
  if (!muteRole) {
    try {
      muteRole = await guild.roles.create({
        data: {
          name: 'Muted',
          permissions: []
        }
      });
    } catch (err) {
      client.logger.error(err.message);
    }
    for (const channel of guild.channels.cache.values()) {
      try {
        if (channel.viewable && channel.permissionsFor(guild.me).has('MANAGE_ROLES')) {
          if (channel.type === 'text') // Deny permissions in text channels
            await channel.updateOverwrite(muteRole, {
              'SEND_MESSAGES': false,
              'ADD_REACTIONS': false
            });
          else if (channel.type === 'voice' && channel.editable) // Deny permissions in voice channels
            await channel.updateOverwrite(muteRole, {
              'SPEAK': false,
              'STREAM': false
            });
        }
      } catch (err) {
        client.logger.error(err.stack);
      }
    }
  }
}