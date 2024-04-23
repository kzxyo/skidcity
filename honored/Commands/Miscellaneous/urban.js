const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const moment = require('moment');

module.exports = {
    configuration: {
        commandName: 'urban',
        aliases: ['ud'],
        description: 'Shows the definition of a word from Urban Dictionary',
        syntax: 'urban [word]',
        example: 'urban discord',
        permissions: 'N/A',
        parameters: 'word',
        module: 'miscellaneous'
    },

    run: async (session, message, args) => {
        const word = args.join(' ');

        if (!word) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            const response = await axios.get(`http://api.urbandictionary.com/v0/define?term=${word}`);
            const json = response.data;

            if (!json.list || json.list.length === 0) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: No definition found for **${word}**`)
                    ]
                });
            }

            const data = json.list[0];
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setTitle(data.word)
                        .setURL(data.permalink)
                        .setDescription(`${data.definition}`)
                        .addFields(
                            { name: "Example", value: `${data.example}`, inline: false }
                        )
                ]
            });
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: API returned an error`)
                ]
            });
        }
    }
};
