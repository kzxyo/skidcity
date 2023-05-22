const Discord = require("discord.js");
const db = require("quick.db")
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "logs",
  aliases: ['modlogs'],

  run: async (client, message, args) => {

    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });

    let prefix = db.get(`prefix_${message.guild.id}`)
    const args1 = message.content.trim().split(/ +/g)
    if (prefix === null) { prefix = default_prefix; }

    let channel2 = args[0]

    if(!channel2) {
        const logsEmbed = new Discord.MessageEmbed()
        .setColor(color)
        .setTitle(`${prefix}logs`)
        .setDescription(`set your server modlogs`)
        .addField(`**subcommands**`, `${prefix}logs channel ＊ set your modlogs channel\n${prefix}logs clear ＊ remove the current modlog channel`)
        .addField(`**usage**`, `${prefix}logs`)
        .addField(`**aliases**`, `modlogs`)

        message.channel.send(logsEmbed)
    }

    if (args[0] == "clear") {
      db.delete(`logschannel_${message.guild.id}`)
     return await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: The previous **modlogs channel** has been removed`}})
    }

    if (args[0] == "channel") {
    let channel = message.mentions.channels.first()
    if(!channel) {
        return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: To set the modlogs channel do \`${prefix}logs channel [channel]\``}})
    }
    db.set(`logschannel_${message.guild.id}`, channel.id)
  await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Set the **modlogs channel** to ${channel}`}})
    
  }
}}