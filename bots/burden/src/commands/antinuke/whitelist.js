const { MessageEmbed } = require("discord.js"),
  db = require('../../core/db');

module.exports = {
  name: 'trust',
  aliases: ['wl', 'whitelist'],
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
            .setDescription('**whitelist**\nmake users immune to the antinuke module\n\n﹒**usage** - whitelist @user\n﹒: requires server ownership');
          
          message.channel.send({ embeds: [guide] });
          
        } else {
          const ID = user.id;
          const whitelisted = await db.get(`${message.guild.id}_wl_${user.id}`);

          if (whitelisted) {
            message.channel.send({ content: `user already whitelisted` });
          } else {
            await db.set(`${message.guild.id}_wl_${ID}`, true)
            await message.reply({ content: `:thumbsup:` })
          }
        }
      } else {
        message.channel.send({ content: `enable antinuke module to use this command` });
      }
    }
  },
}