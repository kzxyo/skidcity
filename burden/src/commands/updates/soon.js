const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "coming",
  aliases: ['wip', 'comingsoon', 'soon'],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setDescription("coming soon: `documentation site`")
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};