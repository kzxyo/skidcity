const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'shuffle',
        aliases: ['shuf'],
        description: "Shuffle the order of the queue.",
        syntax: 'shuffle',
        example: 'shuffle',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'music'
    },
    run: async (session, message, args) => {
        if (!message.member.voice.channel) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You must be in a **voice channel**`)
                        .setColor(session.warn)
                ]
            });
        }
        
        const voiceChannel = message.member.voice.channel;
        const queue = session.player.getQueue(message);
        
        if (!queue || !queue.songs || queue.songs.length === 0) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: There is nothing in the queue to shuffle`)
                        .setColor(session.warn)
                ]
            });
        }

        if (voiceChannel.id !== message.guild.me.voice.channel?.id) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You are not in my **voice channel**`)
                        .setColor(session.warn)
                ]
            });
        }

        queue.shuffle();
        
        return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.grant} ${message.author}: Queue has been shuffled`)
                    .setColor(session.green)
            ]
        });
    },
};
