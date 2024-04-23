const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'seek',
        aliases: ['none'],
        description: 'Skip to a certain time in the song',
        syntax: 'seek <time>',
        example: 'seek 1:30',
        permissions: 'N/A',
        parameters: 'time',
        module: 'music'
    },

    run: async (session, message, args) => {
        let voiceChannel = message.guild.me.voice.channel
        if (voiceChannel) {
            if (voiceChannel.id && message.member.voice.channel.id !== voiceChannel.id) return message.channel.send({ embeds: [
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
        if (!args[0]) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: Please provide a time to seek to`)
                .setColor(session.warn)
        ]})

        const timeToSeconds = (timeString) => {
            const [minutes, seconds] = timeString.split(':').map(Number);
            return minutes * 60 + seconds;
        };

        const timeInSeconds = timeToSeconds(args[0]);
        await session.player.seek(message, timeInSeconds);
        message.channel.send(`👍`);
    }
};
