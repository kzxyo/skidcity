const { MessageEmbed, Permissions } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'clearsnipe',
        description: 'Clears the snipes for the current channel',
        aliases: ['cs'],
        syntax: 'clearsnipe',
        example: 'clearsnipe',
        permissions: 'manage_messages',
        parameters: 'N/A',
        module: 'servers'
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_MESSAGES')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                        .setColor(session.warn)
                ]
            });
        }

        
        const snipes = session.snipes.get(message.channel.id);
        if (!snipes || snipes.length === 0) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no snipes to clear in this channel`)]
            });
        }
        
        session.snipes.delete(message.channel.id);
        
        message.channel.send({
            embeds: [
                new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: Snipes have been cleared for this channel`)]
        });
    }
};
