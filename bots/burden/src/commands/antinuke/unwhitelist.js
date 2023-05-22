const { MessageEmbed } = require("discord.js"),
  db = require('../../core/db');

module.exports = {
  name: 'untrust',
  aliases: ['unwhitelist', 'uwl'],
  run: async (client, message, args) => {
    if (message.author.id !== message.guild.ownerId) {
      message.channel.send({ content: `*This command is only for the server owner` });
    } else {
      const enabled = await db.get(`${message.guild.id}_antinuke`);
      if (enabled === true) {
        const user = message.mentions.users.first();
        if (!user) {
          const guide = new MessageEmbed()
            .setColor("#2F3136")
            .setDescription("**unwhitelist**\n*you can unwhitelist users by this using this command.*\n\n﹒**usage** - unwhitelist @user\n﹒: requires server ownership");

          message.reply({ embeds: [guide] })

        } else {
          const ID = user.id;
          const whitelisted = await db.get(`${message.guild.id}_wl_${user.id}`);

          if (!whitelisted) {
            message.reply({ content: `that user is not whitelisted` });
          } else {
            await db.delete(`${message.guild.id}_wl_${ID}`)
            await message.reply({ content: `**${user.username}** is now unwhitelisted` })
          }
        }
      } else {
        message.reply({ content: `enable the antinuke module first` });
      }
    }
  },
}