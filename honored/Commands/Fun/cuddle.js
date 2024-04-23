const { MessageEmbed } = require('discord.js');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'cuddle',
        aliases: ['none'],
        description: 'cuddle a server member',
        syntax: 'cuddle <member>',
        example: 'cuddle @x6l',
        permissions: 'N/A',
        parameters: 'member',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first();

        if (!user) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Please mention a user to **cuddle**`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            const { data } = await axios.get('https://nekos.life/api/v2/img/cuddle');

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setTitle(`${message.author.username} cuddles ${user.user.username}`)
                        .setURL(data.url)
                        .setImage(data.url)
                        .setColor(session.color)
                ]
            });
        } catch (error) {
            console.error('Error fetching cuddle image/gif:', error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`An error occurred while fetching the cuddle image/gif: ${error.message}`)
                        .setColor(session.warn)
                ]
            });
        }
    }
};
