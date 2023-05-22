const { MessageEmbed } = require("discord.js");

module.exports = {
  name: "updates",
  aliases: ['new', 'newest', 'update'],
  run: async (client, message, args) => {;
    const ping = new MessageEmbed()
      .setColor("#2F3136")
      .setDescription("newest update: `;perks ;donate ;socials`")
    // Sending
    message.channel.send({ embeds: [ping]});
  },
};