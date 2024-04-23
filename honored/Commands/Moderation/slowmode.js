const { MessageEmbed, Permissions } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'slowmode',
        aliases: ['sm'],
        description: 'Set the slowmode of a channel',
        syntax: 'slowmode [time]',
        example: 'slowmode 10s',
        permissions: 'manage_channels',
        parameters: 'duration',
        module: 'moderation',
        devOnly: false
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_channels\``)
                        .setColor(session.warn)
                ]
            });
        }

        if (!args.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        let slowmode;
        const time = args[0].toLowerCase();
        if (time.endsWith('s')) {
            slowmode = parseInt(time);
        } else if (time.endsWith('m')) {
            const minutes = parseInt(time.slice(0, -1));
            slowmode = minutes * 60;
        } else if (time.endsWith('h')) {
            const hours = parseInt(time.slice(0, -1));
            slowmode = hours * 60 * 60;
        } else {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Please provide a valid time format (10s, 1m, 2h)`)
                        .setColor(session.warn)
                ]
            });
        }

        if (isNaN(slowmode) || slowmode < 0 || slowmode > 21600) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Please provide a valid time within the range of **0s** to **6h**`)
                        .setColor(session.warn)
                ]
            });
        }

        await message.channel.setRateLimitPerUser(slowmode);
        message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.grant} ${message.author}: Slowmode has been set to **${slowmode}** seconds`)
                    .setColor(session.green)
            ]
        });
    }
};
