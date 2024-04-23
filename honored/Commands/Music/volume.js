const { MessageEmbed } = require('discord.js');


module.exports = {
    configuration: {
        commandName: 'volume',
        aliases: ['vol'],
        usage: '[0-100]',
        description: "Change the music player's volume.",
        syntax: 'volume [volume]',
        example: 'volume 50',
        permissions: 'N/A',
        parameters: 'volume',
        module: 'music'
    },
    run: async (session, message, args) => {

        let voiceChannel = message.guild.me.voice.channel
        if (voiceChannel) {
            if (voiceChannel.id && message.member.voice.channel.id !== voiceChannel.id) return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You are not in my voice channel`)
                        .setColor(session.warn)
                ]
            });
        }
        if (message.guild.me.voice.channel.id && message.member.voice.channel.id !== message.guild.me.voice.channel.id) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You are not in my voice channel`)
                    .setColor(session.warn)
            ]
        });
        const amount = Number(args[0]);
        const queue = session.player.getQueue(message)
        if (!queue) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}:  There is nothing playing`)
                    .setColor(session.warn)
            ]
        })
        if (!amount) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`:loud_sound: ${message.author}: The current volume is **\`${queue.volume}%\`**`)
                    .setColor(session.color)
            ]
        });
        if (amount < 0) {
            amount = 0;
            var total = 100;
            var current = amount;
            const embed = new MessageEmbed()
                .setDescription(`:notes: ${message.author}: Successfully set the volume to **\`${amount}%\`**`)
                .setColor(session.color)
            return message.channel.send({ embeds: [embed] })
        }
        if (amount > 10000000000) {
            const embed = new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: Cant set the volume to a number above \`10000000000\``)
                .setColor(session.warn)
            message.channel.send({ embeds: [embed] })
        } else {
            session.player.setVolume(message, amount);
            var total = 100;
            var current = amount;
            const embed = new MessageEmbed()
                .setDescription(`${session.grant} ${message.author}: Successfully set the volume to **\`${amount}%\`**`)
                .setColor(session.green)
            message.channel.send({ embeds: [embed] })
        }
    },
};