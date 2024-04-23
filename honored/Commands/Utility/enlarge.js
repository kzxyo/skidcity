const { MessageEmbed, Util } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'jumbo',
        aliases: ['e', 'enlarge'],
        description: 'Enlarge an emoji.',
        syntax: 'enlarge <emoji>',
        example: 'enlarge :rofl:',
        module: 'utility'
    },
    run: async (session, message, args) => {
        const emoji = args[0];

        if (!emoji) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                .setTitle('Command: enlarge')
                .setDescription('Enlarge an emoji.\n```Syntax: enlarge <emoji>\nExample: enlarge :rofl:```');

            return message.channel.send({ embeds: [embed] });
        }

        let custom = Util.parseEmoji(emoji);
        const embed = new MessageEmbed()
            .setColor(session.color);

        if (custom.id) {
            embed.setImage(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`);
            return message.channel.send({ embeds: [embed] });
        } else {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: That's not a custom emoji`)
            ]});
        }
    }
};
