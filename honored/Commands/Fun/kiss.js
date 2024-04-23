const { MessageEmbed } = require('discord.js');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'kiss',
        aliases: ['none'],
        description: 'Kiss a server member',
        syntax: 'kiss <member>',
        example: 'kiss @x6l',
        parameters: 'member',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first();

        if (!user) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Please mention a user to **kiss**`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            const { data } = await axios.get('https://nekos.life/api/v2/img/kiss');

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setTitle(`${message.author.username} kissed ${user.user.username}`)
                        .setURL(data.url)
                        .setImage(data.url)
                        .setColor(session.color)
                ]
            });
        } catch (error) {
            console.error('Error fetching kiss image/gif:', error);
        }
    }
};
