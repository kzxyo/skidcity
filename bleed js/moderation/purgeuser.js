const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "purgeuser",
  aliases: ["puser"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\`` } });
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\`` } });
    const purgehelpEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: purgeuser')
      .setDescription('Deletes the specified amount of messages from the mentioned user')
      .addField('**Aliases**', 'puser', true)
      .addField('**Parameters**', 'member, amount', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: purgeuser (member) <amount>\nExample: purgeuser four#0001 30\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(purgehelpEmbed);

    let member = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    let amount = args[1]
    if (!member) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You need to **mention** a user to purge` } })
    if (!amount) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: Provide an **amount** to purge` } })
    if (isNaN(amount)) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You need to enter a **valid** amount to purge` } })
    if (amount > 100) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: Invalid amount. Make sure it is between **2-100**` } })
    let AllMessages = await message.channel.messages.fetch()
    let FilteredMessages = await AllMessages.filter(x => x.author.id === member.id)
    let deletedMessages = 0
    FilteredMessages.forEach(msg => {
      if (deletedMessages >= amount) return
      msg.delete()
      deletedMessages++
    })
  }
}