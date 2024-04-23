const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'pause',
        aliases: ['pa'],
        description: 'Pause the current music.',
        syntax: 'pause',
        example: 'pause',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'music'
    },
    run: async (session, message, args) => {
        let voiceChannel = message.guild.me.voice.channel;
        if (voiceChannel) {
            if (voiceChannel.id && message.member.voice.channel.id !== voiceChannel.id) return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You are not in my voice channel`)
                        .setColor(session.warn)
                ]
            });
        }
        let queue = session.player.getQueue(message);
        if (!queue) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: There is nothing playing`)
                    .setColor(session.warn)
            ]
        });
        await session.player.pause(message);
        message.channel.send(`👍`);
    }
}