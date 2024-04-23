const axios = require('axios');
const qs = require('qs');
const moment = require('moment-timezone');
const geo = require('geo-tz');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'timezone',
        aliases: ['tz'],
        description: 'View a location\'s timezone',
        syntax: 'timezone [city]',
        example: 'timezone chicago',
        permissions: 'N/A',
        parameters: 'city',
        module: 'utility'
    },

    run: async (session, message, args) => {
        try {
            const query = args.join(' ');

            if (!query) {
                return displayCommandInfo(module.exports, session, message);
            }

            const queryString = qs.stringify({
                q: query,
                limit: 1,
                appid: '985f10d327f3695fa10aab134e0b6391'
            });

            const response = await axios.get(`http://api.openweathermap.org/geo/1.0/direct?${queryString}`);

            const results = response.data;

            if (!results || results.length === 0) {
                const errorEmbed = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Location \`${query}\` not found`);
                return message.channel.send({ embeds: [errorEmbed] });
            }

            const location = geo.find(results[0].lat, results[0].lon)[0];
            const time = moment.tz(new Date(), location).format('hh:mm A');

            const timezoneEmbed = new MessageEmbed()
                .setColor('#748cdc')
                .setDescription(`:mag: ${message.author}: It is currently **${time}** in **${query}**`);
            message.channel.send({ embeds: [timezoneEmbed] });
        } catch (error) {
            session.log('Error:', error.message);
            const errorEmbed = new MessageEmbed()
                .setTitle('Command: timezone')
                .setColor(session.color)
                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                .setDescription('View the timezone in a city\n```Syntax: timezone [city]\nExample: timezone chicago```');
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
