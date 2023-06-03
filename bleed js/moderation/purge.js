const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "purge",
  aliases: ["clear", "prune", "c"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\`` } });
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\`` } });
    const purgehelpEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: purge')
      .setDescription('Deletes the specified amount of messages from the current channel')
      .addField('**Aliases**', 'clear, prune, c', true)
      .addField('**Parameters**', 'member, amount', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: purge <amount>\nExample: purge 30\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(purgehelpEmbed);
    const amountToDelete = Number(args[0], 10);
    if (isNaN(amountToDelete)) return message.channel.send('Make sure you put in a number. Do \`purge\` to see the variables');
    if (!Number.isInteger(amountToDelete)) return message.channel.send('Make sure you put in a number and not an integer. Do \`purge\` to see the variables');
    if (!amountToDelete || amountToDelete < 2 || amountToDelete > 100) return message.channel.send('Invalid amount. Make sure it is between **2-100**')
    const fetched = await message.channel.messages.fetch({
      limit: amountToDelete
    });

    try {
      await message.channel.bulkDelete(fetched)
      return message.channel.send(`Purged **${fetched.size}** messages 👍`).then(msg => {
        msg.delete({ timeout: 1000 })
      })
    } catch (err) {
      console.log(err);
      return message.channel.send('Unable to **purge**')
    }
  }
}