const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
      commandName: 'serverbanner',
      aliases: ['sbanner'],
      description: 'Show the server banner.',
      syntax: 'serverbanner [invite]',
      example: 'serverbanner okay',
      permissions: 'N/A',
      parameters: 'vanity',
      module: 'information',
      devOnly: false
    },
    run: async (session, message, args) => {
      let guildBanner;
      let guildName;

      if (args.length > 0) {
        const inviteCode = args[0];
        const invite = await session.fetchInvite(`https://discord.gg/${inviteCode}`).catch(() => null);
  
        if (invite && invite.guild) {
          guildBanner = invite.guild.bannerURL({ dynamic: true, size: 4096 }) || null;
          guildName = invite.guild.name;
        } else {
          return message.channel.send({ embeds: [
            new MessageEmbed()
              .setDescription(`${session.mark} ${message.author}: Couldn't find a server with the URL [\`${inviteCode}\`](https://discord.com/invite/${inviteCode})`)
              .setColor(session.warn)
          ]});
        }
      } else {
        guildBanner = message.guild.bannerURL({ dynamic: true, size: 4096 }) || null;
        guildName = message.guild.name;
      }
  
      if (!guildBanner) {
        return message.channel.send({ embeds: [
          new MessageEmbed()
            .setDescription(`${session.mark} ${message.author}: That server does not have a banner`)
            .setColor(session.warn)
        ]})
      }
  
      message.channel.send({ embeds: [
        new MessageEmbed()
          .setColor(session.color)
          .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true, size: 2048 }))
          .setTitle(`${guildName}'s banner`)
          .setURL(guildBanner)
          .setImage(guildBanner)
      ] });
    },
};
