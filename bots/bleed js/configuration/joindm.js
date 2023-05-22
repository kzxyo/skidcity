const Discord = require('discord.js')
const db = require('quick.db')
const schema = require('../../models/joindmmodel')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "joindm",
  aliases: ['jdm', 'welcomedm'],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\`` } });

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;
    const sub = args[0]
    const embed = new Discord.MessageEmbed()
      .setTitle(`**${prefix}joindm**`)
      .setDescription(`set up a join dm when new members join`)
      .addField(`**subcommands**`, `${prefix}joindm message ＊ edit the join dm, text\n${prefix}joindm clear ＊ clear the join dm message\n${prefix}joindm test ＊ test how the join dm will look\n${prefix}joindm variables ＊ list all the join dm variables`)
      .addField(`**usage**`, `${prefix}joindm`)
      .addField(`**aliases**`, `jdm, welcomedm`)
      .setColor(color)
    if (!sub) return message.channel.send(embed)

    if (sub === 'message') {
      const msg = args.slice(1).join(" ")
      const state = new Discord.MessageEmbed()
        .setDescription(`${warn} ${message.author}: You need to provide a **join message**`)
        .setColor(`#efa23a`)
      if (!msg) return message.channel.send(state)

      schema.findOne({ guildId: message.guild.id }, async (err, data) => {
        if (data) {
          data.Message = msg
          data.save();
        } else {
          new schema({
            guildId: message.guild.id,
            Message: msg,
          }).save()
        }
      })
      return message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set your **joindm message**` } })
    }

    if (sub === 'clear') {
      const msg = args.slice(1).join(" ")
      schema.findOne({ guildId: message.guild.id }, async (err, data) => {
        if (!data) {
          return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There is no **joindm message** set for me to clear this` } })
        } else {
          await schema.findOneAndDelete({ guildId: message.guild.id });
        }
        return message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Successfully cleared the **joindm message**` } })
      })
    }
    if (sub === 'test') {
      const msg = args.slice(1).join(" ")
      schema.findOne({ guildId: message.guild.id }, async (err, data) => {
        if (!data) {
          return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There is no **joindm message** set for me to test this` } })
        } else {
          message.channel.send(data.Message)
        }
      })
    }
  }
}