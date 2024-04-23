const { MessageEmbed } = require("discord.js");
const axios = require("axios");

module.exports = {
    configuration: {
        commandName: 'litecoin',
        aliases: ['ltc'],
        description: 'Get the current Litecoin price',
        syntax: 'litecoin',
        example: 'litecoin',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const api_url = 'https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true';
            const response = await axios.get(api_url);
            const { litecoin } = response.data;

            const change = parseFloat(litecoin.usd_24h_change).toFixed(2);

            const embed = new MessageEmbed()
                .setColor('#345c9c')
                .setAuthor('Litecoin', 'https://cdn.discordapp.com/attachments/1145561681158737930/1208855545440895028/litecoin-ltc-logo.png?ex=65e4cd75&is=65d25875&hm=f798e5fe21d33e3668ec323fbe2168ace77c03f1ded1158d00d70809da4d82d0&')
                .setDescription(`**$${litecoin.usd} USD (${change}%)**`)
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
