// Button Pagination and Discord.js
const { Message, Client, MessageActionRow, MessageButton } = require("discord.js");
const client = require("../../index");

const Settings = require("../../core/settings");

// Command
module.exports = {
  name: "invite",
  aliases: ['i', 'inv'],
  run: async (client, message, args) => {
    const button = new MessageActionRow().addComponents(
      new MessageButton()
        .setLabel("invite me")
        .setStyle("LINK")
        .setURL(`https://discord.com/oauth2/authorize?client_id=1013566529473888309&permissions=8&scope=bot`)
    )
    
    // Sending
    message.channel.send({
      content: "`click the button invite me`", 
      components: [button] });
  },
};