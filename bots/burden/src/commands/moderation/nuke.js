const { MessageEmbed, MessageActionRow, MessageButton } = require('discord.js');

const client = require('../../index');
const db = require('../../core/db');

module.exports = {
  name: "nuke",
  aliases: ['n'],
  run: async (client, message, args) => {
    if (!message.member.permissions.has('MANAGE_CHANNELS')) {
      message.reply({
        content: 'You need **MANAGE_CHANNELS** permissions to do that'
      })
    } else {
    const channel = message.mentions.channels.first() || message.channel;


    const embed = new MessageEmbed()
    .setColor('#2F3136')
    .setDescription(`> are you sure you want to nuke this channel?`);

    const button = new MessageActionRow().addComponents(
      new MessageButton()
      .setLabel('yes')
      .setCustomId('nYes')
      .setStyle('SUCCESS')
    )
      await db.set(`nuke_${message.author.id}`,channel.id);
      message.channel.send({
        embeds: [embed],
        components: [button]
      }).then((m) => {
        setTimeout(async () => {
          m.delete();
          await db.delete(`nuke_${message.author.id}`);
        }, 3000)
      })
    }
  }
}

client.on('interactionCreate', async (i) => {
  const author = await db.get(`nuke_${i.user.id}`);
  if (i.isButton()) {
    if (author === null) {
      i.reply({
        content: 'This button is not for you',
        ephemeral: true,
      });
    } else {
      const channel = i.guild.channels.cache.find(c => c.id == author);
      if (channel) {
        channel.delete()
        channel.clone().then((c) => {
          c.send('💣')
        })
      }
    }
  }
})