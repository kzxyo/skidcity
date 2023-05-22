// Button Pagination and Discord.js
const { Message, Client, MessageActionRow, MessageButton } = require("discord.js");
const client = require("../../index");

const Settings = require("../../core/settings");

// Command
module.exports = {
  name: "syntax",
  aliases: ['usage', 'usages', 'docs'],
  run: async (client, message, args) => {
    const button = new MessageActionRow().addComponents(
      new MessageButton()
        .setLabel("docs")
        .setStyle("LINK")
    .setURL(`https://discord.gg/burden`)
    )
    
    // Sending
    message.channel.send({
      content: "click the button", 
      components: [button] });
  },
};