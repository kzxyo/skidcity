const yts = require('yt-search');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
  configuration: {
    commandName: 'youtube',
    aliases: ['yt'],
    description: 'Searches youtube for video query',
    syntax: 'youtube [query]',
    example: 'youtube Fortnite',
    permissions: 'N/A',
    parameters: 'query',
    module: 'miscellaneous'
  },
  run: async (session, message, args) => {
    if (args.length < 1) {
      return displayCommandInfo(module.exports, session, message);
    }
    const query = args.join(' ');

    try {
      const videoResults = await yts(query);

      if (videoResults.videos.length > 0) {
        const firstVideo = videoResults.videos[0];

        message.channel.send({ content: `https://www.youtube.com/watch?v=${firstVideo.videoId}` });
      } else {
        message.channel.send({
          embeds: [
            new MessageEmbed()
              .setColor(session.warn)
              .setDescription(`${session.mark} ${message.author}: Couldn't find results for that query`)
          ]
        });
      }
    } catch (error) {
      session.log('Error:', error.message);
      message.channel.send({
        embeds: [
          new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: Couldn't find results for that query`)
        ]
      });
    }
  },
};
