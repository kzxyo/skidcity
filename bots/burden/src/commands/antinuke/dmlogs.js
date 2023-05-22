const { MessageEmbed } = require('discord.js'),
  st = require('../../core/settings').bot,
  db = require('../../core/db.js');


module.exports = {
  name: 'dmlogs',
  aliases: ['dm', 'logging'],
  run: async (client, message, args) => {
    const antinuke = await db.get(`${message.guild.id}_antinuke`);
    if (antinuke) {
    let prefix = await db.get(`${message.guild.id}_prefix`);
    if (!prefix) prefix = st.info.prefix;
    
    const guide = new MessageEmbed()
      .setColor(';antinuke')
      .setDescription(`**dm logger**

**commands:**
- to enable dm Logging: ${prefix}dmlogs enable
- to disable dm Logging: ${prefix}dmlogs disable

**if logging is enabled:**
- info of unauthorized actions will ve sent in dms.
- this info will be sent to the server owner only.`);

    const option = args[0];
    const isActivatedAlready = await db.get(`${message.guild.id}_dmlogs`);

    if (message.author.id === message.guild.ownerId) {
      if (!option) {
        message.reply({ embeds: [guide] });
      } else if (option === 'enable') {
        if (isActivatedAlready) {
          message.reply(`the dmlogs modules is already enabled`)
        } else {
          await db.set(`${message.guild.id}_dmlogs`, true);
          message.reply(`:thumbsup:`);
        }
      } else if (option === 'disable') {
        if (!isActivatedAlready) {
          message.reply(`the dmlogs module is already disabled`)
          } else {
              await db.delete(`${message.guild.id}_dmlogs`);
              message.reply(`:thumbsup:`);
            }
          }
        } else {
          message.reply({ embeds: [guide] });
        }
      } else {
      message.reply('to use this command, you need to enable the antinuke')
    }
  }
}