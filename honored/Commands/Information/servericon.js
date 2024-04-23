const { MessageEmbed } = require('discord.js');

module.exports = {
  configuration: {
    commandName: 'servericon',
    aliases: ['icon', 'sicon'],
    description: 'Show the server icon.',
    syntax: 'servericon [invite]',
    example: 'servericon okay',
    permissions: 'N/A',
    parameters: 'vanity',
    module: 'information',
    devOnly: false
  },
  run: async (session, message, args) => {
    let guildIcon;
    let guildName;

    if (args.length > 0) {
      const inviteCode = args[0];
      const invite = await session.fetchInvite(`https://discord.gg/${inviteCode}`).catch(() => null);

      if (invite && invite.guild) {
        guildIcon = invite.guild.iconURL({ dynamic: true, size: 4096 }) || null;
        guildName = invite.guild.name;
      } else {
        return message.channel.send({
          embeds: [
            new MessageEmbed()
              .setDescription(`${session.mark} ${message.author}: Couldn't find a server with the URL [\`${inviteCode}\`](https://discord.com/invite/${inviteCode})`)
              .setColor(session.warn)
          ]
        });
      }
    } else {
      guildIcon = message.guild.iconURL({ dynamic: true, size: 4096 }) || null;
      guildName = message.guild.name;
    }

    if (!guildIcon) {
      return message.channel.send({
        embeds: [
          new MessageEmbed()
            .setDescription(`${session.mark} ${message.author}: That server does not have an icon`)
            .setColor(session.warn)
        ]
      });
    }

    message.channel.send({
      embeds: [
        new MessageEmbed()
          .setColor(session.color)
          .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true, size: 2048 }))
          .setTitle(`${guildName}'s Icon`)
          .setURL(guildIcon)
          .setImage(guildIcon)
      ]
    });
  },
};
