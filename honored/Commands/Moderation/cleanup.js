const { Permissions, MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'cleanup',
        description: 'Purge messages from bots and common prefixes.',
        syntax: 'cleanup',
        example: 'cleanup',
        aliases: ['bc', 'botclear'],
        permissions: 'manage_messages',
        parameters: 'N/A',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
            const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: You're **missing** the \`manage_messages\` permission.`);
            return message.channel.send({ embeds: [errorEmbed] });
        }

        const messages = await message.channel.messages.fetch({ limit: 100 });
        const filteredMessages = messages.filter(msg => (msg.author.bot) || (msg.content.startsWith(',') || msg.content.startsWith('&') || msg.content.startsWith(';') || msg.content.startsWith('!') || msg.content.startsWith('?') || msg.content.startsWith(session.prefix)));

        try {
            await message.channel.bulkDelete(filteredMessages, true);
        } catch (error) {
            console.error(error);
            const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author} An error occured while purging`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
