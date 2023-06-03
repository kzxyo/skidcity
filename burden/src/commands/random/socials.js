// Button Pagination and Discord.js
const { Message, Client, MessageActionRow, MessageButton } = require("discord.js");
const client = require("../../index");

const Settings = require("../../core/settings");

// Command
module.exports = {
  name: "socials",
  aliases: ['tt', 'tiktok', 'insta', 'spotify', 'social', 'insta', 'ig'],
  run: async (client, message, args) => {
    const button = new MessageActionRow().addComponents(
      new MessageButton()
        .setLabel("ayo.so")
        .setStyle("LINK")
    .setURL(`https://ayo.so/fedded`)
    )
    
    // Sending
    message.channel.send({
      content: "click the button for bot socials", 
      components: [button] });
  },
};