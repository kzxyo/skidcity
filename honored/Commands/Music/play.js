const { MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');


module.exports = {
  configuration: {
    commandName: 'play',
    aliases: ['p'],
    description: "Play some music.",
    syntax: 'play [query]',
    example: 'play NEVEREVER',
    permissions: 'N/A',
    parameters: 'query',
    module: "music",
  },
  run: async (session, message, args) => {
    const text = args.join(" ");
    if (!text) {
      return displayCommandInfo(module.exports, session, message);
    }
    
    const voiceChannel = message.member.voice.channel;
    if (!voiceChannel) {
      return message.channel.send({
        embeds: [
          new MessageEmbed()
            .setDescription(`${session.mark} ${message.author}: You must be in a **voice channel**`)
            .setColor(session.warn)
        ]
      });
    }

    const botVoiceChannel = message.guild.me.voice.channel;
    if (botVoiceChannel && botVoiceChannel !== voiceChannel) {
      return message.channel.send({
        embeds: [
          new MessageEmbed()
            .setDescription(`${session.mark} ${message.author}: You are not in my **voice channel**`)
            .setColor(session.warn)
        ]
      });
    }

    try {
      await session.player.play(message, text);
    } catch (error) {
      message.channel.send({
        embeds: [
          new MessageEmbed()
            .setDescription(`${session.mark} ${message.author}: Error playing the song. Please try again later.`)
            .setColor(session.warn)
        ]
      });
    }
  },
};