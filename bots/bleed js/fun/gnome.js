const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "gnome",

  run: async (client, message, args) => {
    const embed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: gnome')
    .setDescription('Gnome the mentioned user')
    .addField('**Aliases**', 'N/A', true)
    .addField('**Parameters**', 'member', true)
    .addField('**Information**', `N/A`, true)
    .addField('**Usage**', '\`\`\`Syntax: gnome (member)\nExample: gnome four#0001\`\`\`')
    .setFooter(`Module: fun`)
    .setTimestamp()
    .setColor(color)
    if (!args[0]) return message.channel.send(embed)

    message.delete();

    let user = message.mentions.users.first();

    message.channel.send(`${user} Ho ho ho ha ha, ho ho ho he ha. Hello there, old chum. I’m g'not a g'nelf. I’m g'not a g'noblin. I’m a g'nome!! And you’ve been, GNOOOMED!!!`);
  }
}