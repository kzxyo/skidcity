const { MessageEmbed } = require("discord.js");
const axios = require("axios");

module.exports = {
    configuration: {
        commandName: 'ethereum',
        aliases: ['eth'],
        description: 'Get the current Ethereum price',
        syntax: 'ethereum',
        example: 'ethereum',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const api_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true';
            const response = await axios.get(api_url);
            const { ethereum } = response.data;

            const change = parseFloat(ethereum.usd_24h_change).toFixed(2);

            const embed = new MessageEmbed()
                .setColor('#647cec')
                .setAuthor('Ethereum', 'https://cdn.discordapp.com/attachments/1145561681158737930/1208929991253823498/R.png?ex=65e512ca&is=65d29dca&hm=6e3f2c3e35bd183b8c4c6e30bb287fc2380c396bcb16d9f36c1ac6ef671321d8&')
                .setDescription(`**$${ethereum.usd} USD (${change}%)**`)
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
