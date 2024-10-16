const { MessageEmbed } = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "about",
  aliases: ["abt", "pluto", "bi", "info", "botinfo"],

  run: async (client, message, args) => {

    let totalseconds = (client.uptime / 1000);
    let days = Math.floor(totalseconds / 86400);
    totalseconds %= 86400;
    let hours = Math.floor(totalseconds / 3600);
    totalseconds %= 3600;
    let minutes = Math.floor(totalseconds / 60);
    let seconds = Math.floor(totalseconds % 60);

    const servercount = client.guilds.cache.size

    const usercount = client.guilds.cache.map((guild) => guild.memberCount).reduce((p, c) => p + c, 0);

    const embed = new MessageEmbed()
      .setColor(color)
      .setTitle(`***${client.user.username}***`)
      .setDescription(`Bot statistics, developed by **[adrian](https://discord.com/users/1137846765576540171)** & **[winter](https://discord.com/users/596752300756697098)** \n**memory:** ${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)}MB, **commands:** ${client.commands.size}`)
      .addFields(
        { name: '**statistics**', value: `guilds: **${servercount} servers**\nusers: **${usercount.toLocaleString()} members**\nuptime: **${days}d ${hours}h ${minutes}m ${seconds}s**`, inline: true },
        )
      .setTimestamp()
      message.channel.send({ embeds: [embed] })
  }
}