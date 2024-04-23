const axios = require("axios");
const { MessageEmbed } = require('discord.js');

module.exports = {
  configuration: {
    commandName: 'banner',
    aliases: ['none'],
    description: 'View a user\'s banner.',
    syntax: 'banner [user]',
    example: 'banner @x6l',
    parameters: 'member',
    module: 'information',
  },
  run: async (session, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    if (!mentionedMember) {
      const searchName = args.join(' ').toLowerCase();
      mentionedMember = message.guild.members.cache.find(member => 
        member.user.username.toLowerCase() === searchName ||
        member.displayName.toLowerCase() === searchName
      );
    }

    const user = mentionedMember?.user || message.author;

    axios.get(`https://discord.com/api/users/${user.id}`, {
      headers: {
        Authorization: `Bot ${session.token}`
      },
    })
    .then((res) => {
      const { banner } = res.data;

      if (banner) {
        const extension = banner.startsWith("a_") ? ".gif" : ".png";
        const url = `https://cdn.discordapp.com/banners/${user.id}/${banner}${extension}?size=2048`;

        const topRole = message.member.roles.highest;

        const embed = new MessageEmbed()
          .setColor(topRole ? topRole.hexColor : session.color)
          .setTitle(user.username + "'s Banner")
          .setURL(url)
          .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true, size: 2048 }))
          .setImage(url);
        
        message.channel.send({ embeds: [embed] });
      } else {
        message.channel.send({ embeds: [
          new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${user}: There is no banner to display`)
        ]});
      }
    });
  }
};
