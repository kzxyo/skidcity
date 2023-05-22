const client = require('../bleed')
const db = require('quick.db')
const { default_prefix, color } = require("../config.json");
const Discord = require('discord.js')

client.snipes = new Map()
client.on('messageDelete', async function (message, guild) {
  if (message.partial) return
  if (message.channel.type === 'text') {
    if (message.author) {
      client.snipes.set(message.channel.id, {
        content: message.content,
        author: message.author.tag,
        image: message.attachments.first() ? message.attachments.first().proxyURL : null
      })
    }

    let logs = db.get(`logschannel_${message.guild.id}`);
    if (!logs) {
      return;
    }
    if (message.author.bot) return;
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.tag, message.author.displayAvatarURL({ dynamic: true }))
      .setTitle(`Deleted Message`)
      .setDescription(message.content)
      .setFooter(`User ID: ${message.author.id}`)
      .setTimestamp()
      .setColor(`${color}`)
    if (message.image) embed.setImage(message.image)
    if (logs) await db.fetch(`logschannel_${message.guild.id}`).then(await message.channel.send(embed))
  }
})