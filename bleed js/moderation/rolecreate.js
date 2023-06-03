const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "rolecreate",
  aliases: ["rc"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_roles\`` } });
    if (!message.guild.me.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_roles\`` } });


    const rcEmbed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: rolecreate')
    .setDescription('Creates a role with optional color')
    .addField('**Aliases**', 'rc', true)
    .addField('**Parameters**', 'role name, color', true)
    .addField('**Information**', `${warn} Manage Roles`, true)
    .addField('**Usage**', '\`\`\`Syntax: rolecreate <role name> (color)\nExample: rolecreate four #ff0000\`\`\`')
    .setFooter(`Module: moderation`)
    .setTimestamp()
    .setColor(color)
    if (!args[0]) return message.channel.send(rcEmbed)

    if (args.length == 0) {
      return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You don't have enough arguments. Format: role roleName optional: color hex`}});
    }

    const roleName = args.join(' ').trim();

    if (args.length > 1) {

      let possibleHex = null;
      if (roleName.length > 6) { possibleHex = roleName.substr(roleName.length - 6); }
      let wasHex = false;
      if (possibleHex !== null && /^[0-9A-F]{6}$/i.test(possibleHex)) { wasHex = true; }

      const updatedRoleName = wasHex == true ? roleName.replace(possibleHex, '') : roleName;

      if (wasHex) {
        await message.guild.roles.create({
          data: {
            name: updatedRoleName,
            color: possibleHex
          }
        });
      }
      else {
        await message.guild.roles.create({
          data: {
            name: updatedRoleName
          }
        });
      }

      await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Created role **${updatedRoleName}**`}});
    }
    else {
      await message.guild.roles.create({
        data: {
          name: roleName
        }
      });

      await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Created role **${roleName}**`}});
    }
  }
}