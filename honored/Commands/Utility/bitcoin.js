const { MessageEmbed } = require('discord.js');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'bitcoin',
        aliases: ['btc'],
        description: 'Get the current Bitcoin price',
        syntax: 'bitcoin',
        example: 'bitcoin',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const api_url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true';
            const response = await axios.get(api_url);
            const { bitcoin } = response.data;

            const change = parseFloat(bitcoin.usd_24h_change).toFixed(2);

            const embed = new MessageEmbed()
                .setColor('#f4941c')
                .setAuthor('Bitcoin', 'https://images-ext-2.discordapp.net/external/yHX59nUk8_u3zQTfjtjNebPE6NaeGorw8Kbp-K0_gTc/https/cdn.discordapp.com/emojis/1126711156766158879.png')
                .setDescription(`**${bitcoin.usd} USD (${change}%)**`)
                .setFooter('Last Updated')
                .setTimestamp();

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} An error occurred, please contact support`)
            ]});
        }
    }
};
