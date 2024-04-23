const { MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'loop',
        aliases: ['lp'],
        description: 'Loop the current song',
        syntax: 'loop <on/off>',
        example: 'loop on',
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
                        .setDescription(`${session.mark} ${message.author}: There is nothing in the queue to loop`)
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

        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }

        const loopStatus = args[0].toLowerCase();
        if (loopStatus === 'on') {
            queue.setRepeatMode(1);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.grant} ${message.author}: Current song has been looped`)
                        .setColor(session.green)
                ]
            });
        } else if (loopStatus === 'off') {
            queue.setRepeatMode(0);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.grant} ${message.author}: Looping has been turned off`)
                        .setColor(session.green)
                ]
            });
        } else {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Invalid option. Please provide either 'on' or 'off' to toggle looping`)
                        .setColor(session.warn)
                ]
            });
        }
    },
};
