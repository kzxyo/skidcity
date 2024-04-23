const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'uptime',
        aliases: ['none'],
        description: 'Shows bot uptime.',
        syntax: 'uptime',
        example: 'uptime',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'information',
        devOnly: false
    },
    run: async (session, message, args) => {
        let totalSeconds = (session.uptime / 1000);
        let days = Math.floor(totalSeconds / 86400);
        totalSeconds %= 86400;
        let hours = Math.floor(totalSeconds / 3600);
        totalSeconds %= 3600;
        let minutes = Math.floor(totalSeconds / 60);
        let seconds = Math.floor(totalSeconds % 60);

        const embed = new MessageEmbed()
            .setColor('#dc2c44')
            .setDescription(`:alarm_clock: ${message.author}: ${session.user.username} has been running for **${days}d ${hours}h ${minutes}m ${seconds}s**`);

        message.channel.send({ embeds: [embed] });
    }
};
