const { MessageEmbed } = require("discord.js");
const pagination = require("../../Utils/paginator.js");

module.exports = {
    configuration: {
        commandName: 'queue',
        aliases: ['q'],
        description: "Show the current queue.",
        syntax: 'queue',
        example: 'queue',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'music'
    },
    run: async (session, message, args) => {
        
        if (!message.member.voice.channel) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You must be in a **voice channel**`)
                    .setColor(session.warn)
            ]
        })
        let voiceChannel = message.guild.me.voice.channel
        if (voiceChannel) {
            if (voiceChannel.id && message.member.voice.channel.id !== voiceChannel.id) return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You are not in my **voice channel**`)
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
        })
        const list = queue.songs.map((song, id) => `\`${id + 1}.\` **[${song.name}](${song.url})**`)
        const embeds = [];
        for (let i = 0; i < list.length; i += 10) {
            const currentList = list.slice(i, i + 10);
            const embed = new MessageEmbed()
                .setDescription(currentList.join("\n"))
                .setColor(session.color);
            embeds.push(embed);
        }

        if (!list.length) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: There isn't anything playing`)
                    .setColor(session.warn)]
        })

        const embed = new MessageEmbed()
            .setAuthor(`${message.author.username}`, `${message.author.displayAvatarURL({ dynamic: true })}`)
            .setTitle(`Queue`)
            .setDescription(list.slice(0, 10).join("\n"))
            .setColor(session.color);

        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] });
        } else {
            pagination(session, message, embeds, 1, '', `(Page 1 of ${embeds.length})`);
        }
    },
};
