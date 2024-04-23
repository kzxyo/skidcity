const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'botinfo',
        aliases: ['about', 'bi'],
        description: 'Shows information about the bot',
        syntax: 'botinfo',
        example: 'botinfo',
        module: 'information'
    },
    run: async (session, message, args) => {

        const servers = session.guilds.cache.size
        const users = session.guilds.cache.map((guild) => guild.memberCount).reduce((p, c) => p + c, 0)

        message.channel.send({ embeds: [
            new MessageEmbed()
            .setColor(session.color)
            .setAuthor(session.user.username + ' Information', session.user.displayAvatarURL({ dynamic: true }))
            .setDescription(`${session.user.username} is an aesthetic feature rich discord bot`)
            .addField('Statistics', `**Servers:** ${servers}\n**Users:** ${users}\n**Channels:** ${session.channels.cache.size}`, true)
            .addField('Information', `**Library:** Discord.js\n**Latency:** ${session.ws.ping}ms\n**Node.js:** v21.0.0`, true)
            .addField('Developer', `**Name:** x6l\n**Support:** [here](${session.server})\n**Github:** [enlarged](https://github.com/enlarged)`, true)
        ] });
    }
};
