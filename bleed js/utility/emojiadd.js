const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "emojiadd",
  aliases: ["copy"],

  run: (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_EMOJIS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_emojis\`` } });
    if (!message.guild.me.hasPermission("MANAGE_EMOJIS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_emojis\`` } });

    if (!args[0]) {
      const emojiEmbed = new Discord.MessageEmbed()
        .setAuthor(message.author.username, message.author.avatarURL({
          dynamic: true
        }))
        .setTitle('Command: emojiadd')
        .setDescription('Downloads emote and adds to server')
        .addField('**Aliases**', 'copy', true)
        .addField('**Parameters**', 'emoji, characters', true)
        .addField('**Information**', `${warn} Manage Emojis`, true)
        .addField('**Usage**', '\`\`\`Syntax: emojiadd (emoji or url)\nExample: emojiadd cdn.discordapp.com/emojis/768...png\`\`\`')
        .setFooter(`Module: information`)
        .setTimestamp()
        .setColor(color)
      if (!args[0]) return message.channel.send(emojiEmbed)
    }
    for (const emojis of args) {
      const getEmoji = Discord.Util.parseEmoji(emojis);

      if (getEmoji.id) {
        const emojiExt = getEmoji.animated ? '.gif' : '.png';
        const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`;
        message.guild.emojis
          .create(emojiURL, getEmoji.name)
          .then((emoji) =>
            message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Added \`:${emoji.name}:\` to this guild` } })
          );
      }
    }
  }
}