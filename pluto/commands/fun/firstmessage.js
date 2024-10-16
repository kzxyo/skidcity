const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "firstmessage",
  aliases: ['firstmsg'],
  description: `gets the very first message in a channel`,
  usage: '{guildprefix}firstmsg',
  run: async(client, message, args) => {

    const fetchmessages = await message.channel.messages.fetch({
      after: 1,
      limit: 1,
    });
  
    const firstmessage = fetchmessages.first();

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setDescription(`the **first message** in ${message.channel} — [jump](${firstmessage.url})`)
  
    return message.channel.send({ embeds: [embed] })
  }
}