module.exports = {
    configuration: {
        commandName: 'supportserver',
        aliases: ['support'],
        description: 'Shows bot support.',
        syntax: 'support',
        example: 'support',
        module: 'information',
    },
    run: async (session, message, args) => {
        message.channel.send(`${message.author}, join this server for any help or questions — ${session.server}`);
    }
};
