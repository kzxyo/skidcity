const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration :{
        commandName: 'clearqueue',
        aliases: ['cq'],
        description: 'Clear the queue.',
        syntax: 'clearqueue',
        example: 'clearqueue',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'music'
    },

    run: async(session, message, args) => {
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
                        .setDescription(`${session.mark} ${message.author}: There is nothing in the queue to clear`)
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

        queue.songs = [];
        
        return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.grant} ${message.author}: Queue has been cleared`)
                    .setColor(session.green)
            ]
        });
    }
}