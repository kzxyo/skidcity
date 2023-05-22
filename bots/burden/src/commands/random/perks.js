const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "perks",
  aliases: [''],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setDescription("dm [win#0006](https://discord.com/users/837726019032973372/) for the subscriber role once you've invited me")
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};