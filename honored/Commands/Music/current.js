const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'currentsong',
        aliases: ['current'],
        description: "Show the current song playing",
        syntax: 'currentsong',
        example: 'currentsong',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'music'

    },

    run: async (session, message, args) => {
        let voiceChannel = message.guild.me.voice.channel
        if(voiceChannel) {
          if(voiceChannel.id && message.member.voice.channel.id !== voiceChannel.id) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: You are not in my **voice channel**`)
                .setColor(session.warn)
          ]});
        }
        let queue = session.player.getQueue(message);
        if (!queue) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: There is nothing playing`)
                .setColor(session.warn)
        ]})
        let song = queue.songs[0];
        let embed = new MessageEmbed()
        .setColor(session.color)
        .setDescription(`:notes: ${message.author}: **Now Playing** - [${song.name}](${song.url}) \`${song.formattedDuration}\``)
        message.channel.send({ embeds: [embed] });
    }
};