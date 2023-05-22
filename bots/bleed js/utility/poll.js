const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "poll",
  aliases: ["createpoll"],
  category: "utility",

run: async(client, message, args) => {
    let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("EMBED_LINKS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`embed_links\``}});

  const pollEmbed = new Discord.MessageEmbed()
  .setAuthor(message.author.username, message.author.avatarURL({
    dynamic: true
  }))
  .setTitle('Command: poll')
  .setDescription('Create a poll')
  .addField('**Aliases**', 'N/A', true)
  .addField('**Parameters**', 'question', true)
  .addField('**Information**', `${warn} Embed Links`, true)
  .addField('**Usage**', '\`\`\`Syntax: poll <question>\nExample: poll Am I gay?\`\`\`')
  .setFooter(`Module: misc`)
  .setTimestamp()
  .setColor(color)
if(!args[0]) return message.channel.send(pollEmbed);
  let msg = args.slice(0).join(' ');

  let embed = new Discord.MessageEmbed()
    .setColor(user.displayHexColor || color)
    .setTitle(`__**Poll**__`)
    .setDescription(`${msg}`)
    .setAuthor(`Poll created by: ${message.author.username}`, message.author.displayAvatarURL({
      dynamic: true,
      size: 2048
    }))
    .setTimestamp()
    .setFooter(`${message.guild.me.displayName}`);
      
  message.delete();

  message.channel.send(embed).then(messageReaction => {
    messageReaction.react('👍');
    messageReaction.react('👎');
  });
}
}