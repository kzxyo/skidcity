const { EmbedBuilder } = require('/root/rewrite/Utils/embed.js');
const { MessageEmbed, Permissions } = require('discord.js'); 
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'createembed',
        aliases: ['ce'],
        description: 'Create and send a custom embed message.',
        syntax: 'createembed [embed code]',
        example: 'createembed {title: hi}$v{footer: meow}',
        module: 'utility'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                    .setColor(session.warn)
            ]
        });
        try {
            if (!args.length) {
                return displayCommandInfo(module.exports, session, message);
            }

            const embedCode = args.join(' ');

            new EmbedBuilder(message.channel, embedCode, message.author);
        } catch (error) {
            console.error('Error creating embed:', error);
            message.channel.send('An error occurred while creating the embed.');
        }
    }
};
