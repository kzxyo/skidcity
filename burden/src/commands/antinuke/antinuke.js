const { MessageEmbed } = require('discord.js'),
  st = require('../../core/settings').bot,
  db = require('../../core/db.js');


module.exports = {
  name: 'antinuke',
  aliases: ['antiwizz', 'an'],
  run: async (client, message, args) => {
    let prefix = await db.get(`${message.guild.id}_prefix`);
    if (!prefix) prefix = st.info.prefix;
    
    const guide = new MessageEmbed()
      .setColor('#2F3136')
      .setDescription(`**toggle antinuke**\n
**antinuke settings**
- to enable the antinuke: ${prefix}antinuke enable
- to disable the antinuke: ${prefix}antinuke disable`);

    const option = args[0];
    const isActivatedAlready = await db.get(`${message.guild.id}_antinuke`);

    if (message.author.id === message.guild.ownerId) {
      if (!option) {
        message.reply({ embeds: [guide] });
      } else if (option === 'enable') {
        if (isActivatedAlready) {
          message.reply(`the antinuke module is already enabled`)
        } else {
          await db.set(`${message.guild.id}_antinuke`, true);
          message.reply(`:thumbsup:`);
        }
      } else if (option === 'disable') {
        if (!isActivatedAlready) {
          message.reply(`the antinuke module is already disabled`)
        } else {
          await db.delete(`${message.guild.id}_antinuke`);
          message.reply(`:thumbsup:`);
        }
      }
    } else {
      message.reply({ embeds: [guide] });
    }
  }
}