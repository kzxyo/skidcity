const db = require('quick.db');
const { default_prefix } = require("../../config.json");
const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: 'altdentifier',
  aliases: ['ad'],

  run: async (client, message, args) => {
    if (args[0] == 'Altdentifier is disabled') {
      if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
      if (!message.guild.me.hasPermission("KICK_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`kick_members\`` } });

      let prefix = db.get(`prefix_${message.guild.id}`)
      if (prefix === null) { prefix = default_prefix; }
      const embed = new Discord.MessageEmbed()
        .setTitle(`**${prefix}altdentifier**`)
        .setDescription(`set up altdentifier when new accounts join`)
        .addField(`**subcommands**`, `${prefix}altdentifier enable ＊ enables altdentifier for the guild\n ${prefix}altdentifier disable ＊ disables altdentifier for the guild`)
        .addField(`**usage**`, `${prefix}altdentifier`)
        .addField(`**aliases**`, `ad`)
        .setColor(color)
      if (!args[0]) return message.channel.send(embed)

      if (await db.has(`anti-new_${message.guild.id}`) === true) {

        await db.delete(`anti-new_${message.guild.id}`);
        message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Altdentifier is now **disabled**` } })

      } else return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Altdentifier has already been **enabled**` } })
    } else if (args[0] == 'enable') {
      if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
      if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\``}});

      if (await db.has(`anti-new_${message.guild.id}`) === false) {

        await db.set(`anti-new_${message.guild.id}`, true)
        message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Altdentifier is now **enabled**` } })

      } else return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Altdentifier has already been **enabled**` } })
    } else if (args[0] == 'on') {
      if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
      if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\``}});

      if (await db.has(`anti-new_${message.guild.id}`) === false) {

        await db.set(`anti-new_${message.guild.id}`, true)
        message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Altdentifier is now **enabled**` } })

      } else return message.channel.send({ embed: { color: "#a3eb7b", description: `${warn} ${message.author}: Altdentifier has already been **enabled**` } })
    } else if (args[0] == 'off', 'disabled') {
      if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
      if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\``}});

      if (await db.has(`anti-new_${message.guild.id}`) === true) {

        await db.delete(`anti-new_${message.guild.id}`);
        message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Altdentifier is now **disabled**` } })

      } else return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Altdentifier has already been **disabled**` } })
    }
  }
}