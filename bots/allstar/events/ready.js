const fs = require("fs");
const { MessageEmbed } = require('discord.js');
module.exports = {
  event: "ready",
  once: true,
  execute: async (client) => {
    client.readyOn = Date.now()
    // Handle Restart
    const { exec } = require('child_process');
    var restartedEmbed = new MessageEmbed()
      .setColor("#32CD32")
      .setTitle("Bot Restarted <a:Check:1045087654280179783>")
      .setDescription("Everything seems good. The bot has been restarted.")
      .setTimestamp()
      .setFooter({
        text: `${client.user.username}`,
        iconURL: client.user.displayAvatarURL()
      });
    await exec("cat /home/allstar/allstar/rstrt-stat-indtr.num", async (err, stdout, stderr) => {
      if (err) {
        await exec(`echo 0 > /home/allstar/allstar/rstrt-stat-indtr.num`)
      }
      var output = stdout;
      if (output !== "") {
        if (!output.toString().startsWith("1")) return
        var outputArray = output.split(" ");
        var guildID = outputArray[1];
        var channelID = outputArray[2];
        var messageID = outputArray[3];
        var guild = client.guilds.cache.get(guildID);
        var channel = guild.channels.cache.get(channelID);
        var message = await channel.messages.fetch(messageID);
        await message.edit({ embeds: [restartedEmbed] })
        await exec(`echo 0 > /home/nifehsrf/allstar/rstrt-stat-indtr.num`)
      }
    });
    let pingemoji = `<:allstarbadconnection:996700696671948901> `
    console.log("Bot ready ");
    client.user.setPresence({ status: "idle", })
    setInterval(async () => {
     // client.user.setActivity(`${client.guilds.cache.size} Servers & ${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)} Users`, {
         client.user.setActivity(`discord.gg/heist`, {
        type: "LISTENING",
        url: "https://www.twitch.tv/discord"
      })
      var guild = client.guilds.cache.get("1031650118375571537");
      var channel = guild.channels.cache.get("1031653251923329117");
      var message = await channel.messages.fetch("1045334297927753819");
      var embed = require("../commands/usage.js")
      embed = await embed.handler(client);
      if (embed.status === 0) message.edit({ embeds: [embed.embed] })
    }, 100000)
    /*
     client.user.setActivity(`discord.gg/heist`, {
        type: "LISTENING",
        url: "https://www.twitch.tv/discord",
        emoji:"⭐"
      })
*/





  },
};
