const Discord = require('discord.js');
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

/***
* @param {Discord.client} bot the discord bot client.
* @param {Discord.messsage} message the initial message sent by the user.
* @param {array} args an array of arguments
 */

module.exports = {
  name: "botclear",
  aliases: ["bc"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\``}});

    try {
      message.channel.messages.fetch().then(messages => {
        const botMessages = messages.filter(msg => msg.author.bot);
        message.channel.bulkDelete(botMessages);
      });
    } catch (err) {
      return;
    }
    message.delete();

    let botClearEmbed = new Discord.MessageEmbed()
      .setColor("#a3eb7b")
      .setDescription(`${approve} ${message.author}: Removed messages from **bots**`)
    message.channel.send(botClearEmbed);
  }
}