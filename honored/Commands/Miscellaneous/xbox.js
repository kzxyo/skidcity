const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'xbox',
        syntax: 'xbox [username]',
        example: 'xbox Ruined',
        permissions: 'N/A',
        parameters: 'username',
        aliases: ['xb', 'xbl'],
        description: 'View a xbox profile',
        module: 'miscellaneous'
    },

    run: async (session, message, args) => {
        try {
            const gamertag = args.join(' ');

            if (!gamertag) {
                const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
            }

            const url = `https://playerdb.co/api/player/xbox/${encodeURIComponent(gamertag)}`;

            const response = await axios.get(url);

            if (response.status !== 200 || !response.data.success) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Couldn't find an account with that username`)
                ]});
            }

            const player = response.data.data.player;

            const embed = new MessageEmbed()
                .setTitle(player.username)
                .setURL(session.server)
                .addField('Gamerscore', player.meta.gamerscore, true)
                .addField('Account Tier', player.meta.accountTier, true)
                .setImage(player.avatar)
                .setFooter('Xbox', 'https://lains.win/xbox-logo.png')
                .setColor('#047c04');

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error.message);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
