const Discord = require('discord.js')
const db = require('quick.db')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "antiinvite",
  aliases: ["antilinks"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\`` } });

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;
    const embed = new Discord.MessageEmbed()
      .setColor(color)
      .setTitle(`${prefix}antiinvite`)
      .setDescription(`set up anti invite when users send a links`)
      .addField('**subcommands**', `${prefix}antiinvite enable ＊ enable anti invite when links are sent\n${prefix}antiinvite disable ＊ disable anti inivte for the guild`)
      .addField('**usage**', `${prefix}antiinvite`)
      .addField('**aliases**', `antilinks`)
    if (!args[0]) return message.channel.send(embed)

    const antilinks = args[0]
    if (!antilinks || (antilinks !== "enable" && antilinks !== "disable")) {

      if (antilinks === "enable") {
        db.set(`antilink_${message.guild.id}`, 'on')

        const embed_on = new Discord.MessageEmbed()
          .setColor(`#a3eb7b`)
          .setDescription(`${approve} ${message.author}: Antiinvite is now **enabled**`)

        message.channel.send(embed_on)

      } else if (antilinks === "disable") {
        db.set(`antilink_${message.guild.id}`, 'off')

        const embed_off = new Discord.MessageEmbed()
          .setColor(`#a3eb7b`)
          .addDescription(`${approve} ${message.author}: Successfully **disabled** antiinvite for this guild`)

        message.channel.send(embed_off)
      }
    }
  }
}