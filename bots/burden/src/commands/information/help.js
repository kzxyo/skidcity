const { MessageEmbed, MessageActionRow, MessageSelectMenu, MessageButton } = require('discord.js');
const Settings = require('../../core/settings.js');
const client = require('../../index');
const db = require('../../core/db');

module.exports = {
  name: 'help',
  aliases: ['h'],
  run: async (client, message, args) => {
    let prefix = await db.get(`${message.guild.id}_prefix`);
    if (!prefix) prefix = Settings.bot.info.prefix;
    
    const helpEmbed = embeds('help');
    const menuOptions = new MessageActionRow().addComponents(
      new MessageSelectMenu()
        .setCustomId('helpOption')
        .setPlaceholder('  ')
        .addOptions([
          {
            label: 'toggling',
            value: 'toggleCmds',
            description: 'enable/disable'
          },
          {
            label: 'whitelisting',
            value: 'wlCmds',
            description: 'whitelist/unwhitelist'
          },
          {
            label: 'antinuke dms',
            value: 'dmNotifs',
            description: 'dm logger'
          },
          {
            label: 'moderation',
            value: 'modCmds',
            description: 'moderation cmds'
          },
          {
            label: 'misc',
            value: 'RandomCmds',
            description: 'etc'
          },
          {
            label: 'bot info',
            value: 'credits',
            description: 'everything about the bot'
          },
        ])
    )

    const buttons = new MessageActionRow().addComponents(
      new MessageButton()
        .setLabel('invite me')
        .setStyle('LINK')
        .setURL('https://discord.com/oauth2/authorize?client_id=1013566529473888309&permissions=8&scope=bot'),
      new MessageButton()
        .setLabel('support server')
        .setStyle('LINK')
        .setURL(`https://discord.gg/A4qcV9yxWg`)
    )

    message.channel.send({
      embeds: [helpEmbed],
      components: [menuOptions, buttons]
    });

    const filter = (i) => i.isSelectMenu();
    const collector = message.channel.createMessageComponentCollector({ filter, limit: 10 });

    collector.on('collect', async (i) => {
      if (i.user.id !== message.author.id) {
        await i.reply({
          content: 'this menu is not for you.',
          ephemeral: true,
        })
      } else {
        await i.deferUpdate();
        const value = i.values[0];

        if (value === 'toggleCmds') {
          await i.editReply({
            embeds: [embeds('toggle', prefix)],
          })
          
        } else if (value === 'wlCmds') {
          await i.editReply({
            embeds: [embeds('whitelist', prefix)]
          })

         } else if (value === 'RandomCmds') {
          await i.editReply({
            embeds: [embeds('Misc', prefix)]
          })
          
        } else if (value === 'dmNotifs') {
          await i.editReply({
            embeds: [embeds('logger', prefix)]
          })
          
        } else if (value === 'modCmds') {
          await i.editReply({
            embeds: [embeds('x')],
          })
        } else if (value === 'credits') {
          await i.editReply({
            embeds: [new MessageEmbed()
      .setColor('#2F3136')
      .setFooter('est 8/24/22')
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription("**burden**\n\n> owner: `win#0006n`\n> library: `discord.js`")]
          })
        }
      }
    })
  }
}
function embeds(embed, prefix, ping) {
  if (embed === 'help') {
    return new MessageEmbed()
      .setColor('#2F3136')
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription("**burden**\nuse the dropdown menu for command list\n\n**support**\njoin the **[support server](https://discord.gg/burden)** for help with **burden**");
    
  } else if (embed === 'x') {
    return new MessageEmbed()
      .setColor("#2F3136")
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription("**commands:**\n\n> `ban` `kick` `nickname` `timeout` `unban` `nuke`\n\nif you are not whitelisted you cannot perform these")
  } else if (embed === 'toggle') {
    return new MessageEmbed()
    .setColor('#2F3136')
    .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
    .setDescription('**commands:**\n\n> `antinuke enable` `antinuke disable`\n\nif you do not whitelist a user they will be banned by antinuke');

  } else if (embed === 'whitelist') {
    return new MessageEmbed()
      .setColor('#2F3136')
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription('**commands:**\n\n> `whitelist` `unwhitelist` `whitelisted`\n\nwhitelisted users will be ignored by antinuke');
  } else if (embed === 'Misc') {
    return new MessageEmbed()
      .setColor('#2F3136')
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription('**commands:**\n\n> `soon` `new` `donate` `invis` `socials` `ping` `info`');

    
  } else if (embed === 'logger') {
    return new MessageEmbed()
      .setColor('#2F3136')
      .setThumbnail('https://cdn.discordapp.com/avatars/1013566529473888309/8eebfbf26554e6316e6136ef987791ae.png?size=1024')
      .setDescription("**commands:**\n\n> `dmlogs enable` `dmlogs disable`\n\nantinuke logs will be sent the server owner");
  }
};
