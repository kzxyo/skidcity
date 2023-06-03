// Button Pagination and Discord.js
const { Message, Client, MessageActionRow, MessageButton } = require("discord.js");
const client = require("../../index");

const Settings = require("../../core/settings");

// Command
module.exports = {
  name: "invisible",
  aliases: ['invis'],
  run: async (client, message, args) => {
    const button = new MessageActionRow().addComponents(
      new MessageButton()
        .setLabel("url")
        .setStyle("LINK")
    .setURL(`https://media.discordapp.net/attachments/1045112527165587567/1045522340894736567/invis.png`)
    )
    
    // Sending
    message.channel.send({
      content: "#2F3136", 
      components: [button] });
  },
};