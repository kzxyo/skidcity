const { MessageEmbed } = require('discord.js');

module.exports = {
  name: 'about',
  aliases: ['info', 'botinfo', 'app', 'stats', 'bi'],
  run: async (client, message, args) => {
    const everyGuild = client.guilds.cache.map((guild) => guild.memberCount);
    const userCount = everyGuild.reduce((x, y) => x + y);
    
    message.channel.send({
      embeds: [new MessageEmbed()
      .setColor('#010101')
      .setThumbnail("https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024")
      .setDescription(`
> library: discord.js
> guilds: ${client.guilds.cache.size.toLocaleString()}
> users: ${userCount.toLocaleString()}
> owner: win#0006
> server: [here](https://discord.gg/burden)`)]
    })
  }
}
