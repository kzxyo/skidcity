const { Client, Message, MessageEmbed } = require("discord.js");
const { color } = require("../../config.json");

module.exports = {
  name: "firstmessage",
  aliases: ["firstmsg"],
  /**
   * @param {Client} client
   * @param {Message} message
   * @param {String[]} args
   */
  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    const fetchMessages = await message.channel.messages.fetch({
      after: 1,
      limit: 1,
    });
    const msg = fetchMessages.first();

    message.channel.send(
      new MessageEmbed()
        .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
          dynamic: true,
          size: 2048
        }))
        .setTitle(`First Messsage in #${message.channel.name}`)
        .setColor(mentionedMember.displayHexColor || color)
        .setURL(msg.url)
        .setThumbnail(msg.author.displayAvatarURL({ dynamic: true, format: "png", size: 2048 }))
        .setDescription("**Content:** " + msg.content)
        .addField("**Author**", msg.author, true)
        .addField('**Message ID**', msg.id, true)
        .addField('**Sent At**', message.createdAt.toLocaleDateString(), true)
    );
  },
};