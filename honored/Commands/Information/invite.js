module.exports = {
    configuration: {
        commandName: 'invite',
        aliases: ['i'],
        description: 'Invite the bot to your server',
        syntax: 'invite',
        example:'invite',
        module: 'information'
    },

    run: async (session, message, args) => {
        message.channel.send({ content: `https://discord.com/api/oauth2/authorize?client_id=${session.user.id}&permissions=8&scope=bot` })
    }
}