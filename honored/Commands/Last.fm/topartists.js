const fs = require('fs');
const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const filePath = '/root/rewrite/Database/lastfm.json';

module.exports = {
    configuration: {
        commandName: 'topartists',
        aliases: ['topar', 'ta'],
        description: 'View your top artists on LastFM',
        syntax: 'topartists',
        example: 'topartists',
        module: 'lastfm'
    },
    run: async (session, message, args) => {
        const key = session.lastfmkey;
        const mentionedUser = message.mentions.users.first();
        const userID = mentionedUser ? mentionedUser.id : message.author.id;
        const lastfmData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        if (!lastfmData[userID]) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor('#FF0000')
                .setDescription(`<:lastfm:1210618435411775549> ${message.author}: The mentioned user doesn't have a LastFM username set!`)
            ]});
        }

        try {
            const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=${lastfmData[userID]}&api_key=${key}&format=json`);
            const topArtists = data.topartists.artist.slice(0, 10);

            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.author.username, message.author.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                .setTitle(`Top 10 Artists for ${lastfmData[userID]}`)
                .setDescription(topArtists.map((artist, index) => `\`${index + 1}.\` **[${artist.name}](${artist.url})** - \`${artist.playcount}\``).join('\n'));

            return message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send('An error occurred while fetching top artists.');
        }
    }
};
