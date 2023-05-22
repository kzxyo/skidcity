const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "donate",
  aliases: ['buy'],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setTitle("donations")
      .setThumbnail("https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024")
      .setDescription("methods:\n[paypal](https://paypal.me/shakwandalol)\n[cashapp](https://cash.app/$votains)")
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};