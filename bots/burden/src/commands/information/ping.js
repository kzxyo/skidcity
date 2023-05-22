const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "ping",
  aliases: ['p'],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setDescription(`\n**latency** = ${client.ws.ping}ms`)
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};