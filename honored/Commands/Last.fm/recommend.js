const fs = require('fs');
const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const filePath = '/root/lain/lain/Database/extra/lastfm.json';

module.exports = {
    configuration: {
        commandName: 'recommend',
        aliases: ['rec'],
        description: 'Recommend a random track based on your listening history',
        syntax: 'recommend',
        example: 'recommend',
        module: 'lastfm',
    },
    run: async (session, message, args) => {
        try {
            const lastfmData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            const lastfmUsername = lastfmData[message.author.id];
            if (!lastfmUsername) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                        .setColor('#FF0000')
                        .setDescription(`<:lastfm:1210618435411775549> ${message.author}: You don't have a LastFM username set! Run \`lastfm set [username]\``)
                    ]
                });
            }

            const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=${lastfmUsername}&api_key=${session.lastfmkey}&format=json&limit=100`);
            const tracks = data.recenttracks.track;
            const randomTrack = tracks[Math.floor(Math.random() * tracks.length)];
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setDescription(`:notes: ${message.author}: I suggest you **${randomTrack.name}** by **${randomTrack.artist['#text']}**`);

            return message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: An error occurred while fetching a recommendation. Please try again later.`)
                ]
            });
        }
    }
};
