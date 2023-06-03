const client = require('../bleed')
const Discord = require('discord.js')

client.on("guildDelete", guild => {
  const embed = new Discord.MessageEmbed()
    .setDescription(`Left guild: **${guild.name}**, owned by ${guild.owner.user.tag} (\`${guild.id}\`) | **${guild.memberCount}** members`)
    .setColor("e74c3c")
  client.channels.cache.get("868302839947100160").send(embed)
})