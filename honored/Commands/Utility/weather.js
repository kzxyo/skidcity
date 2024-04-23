const fs = require('fs/promises');
const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'weather',
        aliases: ['wthr'],
        description: 'View the weather in a certain location',
        syntax: 'weather [location]',
        example: 'weather Paris',
        permissions: 'N/A',
        parameters: 'location',
        module: 'utility'
    },

    run: async (session, message, args) => {

        try {
            if (!args[0]) {
                const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
            }

            const city = args.join(' ');

            const response = await axios.get(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=985f10d327f3695fa10aab134e0b6391`);
            const data = response.data;

            if (!data || data.cod === '404') {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: No results found for **${city}**`)
                ]});
            }

            const embed = new MessageEmbed()
                .setColor('#748cdc')
                .setTitle(`${data.weather[0].description.charAt(0).toUpperCase() + data.weather[0].description.slice(1)} in ${data.name}, ${data.sys.country}`)
                .setURL(`https://openweathermap.org/city/${data.id}`)
                .setThumbnail(`https://openweathermap.org/img/w/${data.weather[0].icon}.png`)
                .addFields(
                    { name: 'Temperature', value: `${(data.main.temp - 273.15).toFixed(2)} °C / ${((data.main.temp - 273.15) * 9 / 5 + 32).toFixed(2)} °F`, inline: true },
                    { name: 'Wind', value: `${data.wind.speed} mph`, inline: true },
                    { name: 'Humidity', value: `${data.main.humidity}%`, inline: true },
                    { name: 'Sun Rise', value: `<t:${data.sys.sunrise}:t>`, inline: true },
                    { name: 'Sun Set', value: `<t:${data.sys.sunset}:t>`, inline: true },
                    { name: 'Visibility', value: `${(data.visibility / 1000).toFixed(1)} km`, inline: true }
                );

            return message.channel.send({ embeds: [embed] });
        } catch(error) {
            console.error('Error while executing weather command:', error);
            return displayCommandInfo(module.exports, session, message);
        }
    }
}