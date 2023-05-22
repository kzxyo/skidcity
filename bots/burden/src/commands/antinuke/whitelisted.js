const { MessageEmbed, MessageActionRow, MessageButton } = require("discord.js"),
  client = require("../../index"),
  db = require('../../core/db');

module.exports = {
  name: "list",
  aliases: ['l', 'trusted', 'whitelisted'],
  run: async (client, message, args) => {
    if (message.author.id !== message.guild.ownerId) {
      message.reply({ content: `only the server owner can use this` });
    } else {
      var enabled = await db.get(`${message.guild.id}_antinuke`);
      if (enabled === true) {
        const users = [];
        const Guild = message.guild.id;
        // Get all trusted users from a guild
        await db.list(`${message.guild.id}_wl_`).then(async array => {
          if (array.length > 0) {
            for (x in array) {
              const mentions = array[x],
                userId = mentions.split('_')[2],
                user = `<@${userId}> (${userId})`;
              users.push(user);
            }

            const trustedUsers = new MessageEmbed()
              .setDescription(`**whitelisted admins**\n\n${users.join('\n')}`)
              .setColor("#2F3136")

            const btn = new MessageActionRow().addComponents(
              new MessageButton()
                .setLabel("clear list")
                .setStyle("DANGER")
                .setCustomId('clear')
            )
            message.channel.send({
              embeds: [trustedUsers],
            });
          } else {
            message.reply({ content: 'there are no whitelisted users in this server' })
          }
        });
      } else {
        message.reply({ content: `enable the antinuke module to use this` });
      }
    }
  },
};