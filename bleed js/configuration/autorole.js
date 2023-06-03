const db = require('quick.db')
const { default_prefix } = require("../../config.json");
const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
    name: "autorole",    
    aliases: ["ar"],
    
    run: async (client, message, args) => {
      if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
      if (!message.guild.me.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_roles\`` } });

      let prefix = db.get(`prefix_${message.guild.id}`)
      if (prefix === null) { prefix = default_prefix; }
      const embed = new Discord.MessageEmbed()
      .setTitle(`**${prefix}autorole**`)
      .setDescription(`set up autorole when new members join`)
      .addField(`**subcommands**`, `${prefix}autorole set ＊ set the autorole for the guild\n ${prefix}autorole clear ＊ clear the original set autorole`)
      .addField(`**usage**`, `${prefix}autorole`)
      .addField(`**aliases**`, `ar`)
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)
    
      if (!args[0]) {
    const rid = db.get(`autorole_${message.guild.id}`);
    const role = message.guild.roles.cache.find(r => r.id === rid);
    if (!role) {
      return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There is no autorole set`}})
    }
    if(!message.member.hasPermission('MANAGE_GUILD')) {
      return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    }}
  else {
    if (args[0].toLowerCase() == 'set') {
      const attemptedRoleName = args.splice(1).join(' ');
      const roleName = message.guild.roles.cache.find(r => r.name === attemptedRoleName);
      if (!roleName) {
        return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You didn't return an existing role ${attemptedRoleName}`}})
      }
          if(!message.member.hasPermission('MANAGE_GUILD')) {
            return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
          }
          await db.set(`autorole_${message.guild.id}`, roleName.id);
          return message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Autorole is now set to **${roleName.name}**`}})
        }
        else if (args[0].toLowerCase() == 'clear') {
          const roleName = db.get(`autorole_${message.guild.id}`);
          if(!message.member.hasPermission('MANAGE_GUILD')) {
            return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
          }
          await db.delete(`autorole_${message.guild.id}`, roleName.id);
          return message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: The autorole is now **cleared**`}})
        }
    }
}}