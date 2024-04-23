const fs = require('fs');
const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const filePath = '/root/rewrite/Database/lastfm.json';

module.exports = {
    configuration: {
        commandName: 'toptracks',
        aliases: ['ttr', 'ttt'],
        description: 'View your top tracks on LastFM',
        syntax: 'toptracks',
        example: 'toptracks',
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
            const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=${lastfmData[userID]}&api_key=${key}&format=json`);
            const topTracks = data.toptracks.track.slice(0, 10);

            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.author.username, message.author.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                .setTitle(`Top 10 Tracks for ${lastfmData[userID]}`)
                .setDescription(topTracks.map((track, index) => `\`${index + 1}.\` **[${track.name}](${track.url})** by **${track.artist.name}** - \`${track.playcount}\``).join('\n'));

            return message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send('An error occurred while fetching top tracks.');
        }
    }
};
