const { Permissions, MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'timeout',
        aliases: ['to'],
        suntax: 'timeout (user) <duration>',
        example: 'timeout @user 1d',
        description: 'Temporary timeout a member from the server.',
        module: 'moderation',
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                        .setColor(session.warn)
                ]
            });
        }

        const member = message.mentions.members.first();
        const durationString = args[1];
        const duration = parseDuration(durationString);

        if (!member || !durationString || !duration) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            await member.timeout(duration, { reason: `${message.author.tag}: Timed out for ${durationString}` });
            await message.reply(`Timed out ${member} for ${durationString}.`);
        } catch (error) {
            console.error('Error timing out member:', error);
            message.reply(`Couldn't timeout ${member}.`);
        }
    }
};

function parseDuration(durationString) {
    if (!durationString) return null;

    const regex = /(\d+)([smhdw])/;
    const matches = durationString.match(regex);
    if (!matches) return null;

    const [, amount, unit] = matches;
    const multiplier = {
        's': 1000,
        'm': 60000,
        'h': 3600000,
        'd': 86400000,
        'w': 604800000
    };
    return amount * multiplier[unit];
}

