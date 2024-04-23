const { MessageEmbed } = require('discord.js');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'tickle',
        aliases: ['none'],
        description: 'tickle a server member',
        syntax: 'tickle <member>',
        example: 'tickle @x6l',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first();

        if (!user) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Please mention a user to **tickle**`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            const { data } = await axios.get('https://nekos.life/api/v2/img/tickle');

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setTitle(`${message.author.username} tickles ${user.user.username}`)
                        .setURL(data.url)
                        .setImage(data.url)
                        .setColor(session.color)
                ]
            });
        } catch (error) {
            console.error('Error fetching tickle image/gif:', error)
        }
    }
};
