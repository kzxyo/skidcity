const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "supportserver",
  aliases: ['verifylol'],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setThumbnail("https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024")
      .setDescription("ㅤㅤㅤ  \nreact with :tools: for **updates**\nreact with :newspaper: for **status**")
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};