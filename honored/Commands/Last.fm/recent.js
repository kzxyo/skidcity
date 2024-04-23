const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const filePath = '/root/rewrite/Database/lastfm.json';
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'recent',
        aliases: ['recenttracks', 'recentlyplayed'],
        description: 'Shows your most recent tracks',
        syntax: 'recent',
        example: 'recent',
        module: 'lastfm'
    },

    run: async (session, message, args) => {
        let targetUser = message.mentions.members.first() || message.member;
        const userID = targetUser.id;

        const key = session.lastfmkey;
        const lastfmData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        const lastfmUsername = lastfmData[userID];

        if (!lastfmUsername) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor('#FF0000')
                .setDescription(`<:lastfm:1210618435411775549> ${targetUser}: ${targetUser.id === message.author.id ? "You don't have" : "This user doesn't have"} a LastFM username set. run \`lastfm set [username]\` to set one`)
            ]});
        }

        try {
            const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=${lastfmUsername}&api_key=${key}&format=json&limit=20`);
            const recentTracks = data.recenttracks.track;

            if (!recentTracks || recentTracks.length === 0) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${targetUser}: ${targetUser.id === message.author.id ? "You haven't listened" : "This user hasn't listened"} to any track on LastFM yet.`)
                ]});
            }

            const embeds = [];
            for (let i = 0; i < recentTracks.length; i += 10) {
                const tracksChunk = recentTracks.slice(i, i + 10);
                const embed = new MessageEmbed()
                    .setColor(session.color)
                    .setAuthor(message.author.username, message.author.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                    .setTitle(`Recent Tracks for ${lastfmUsername}`)
                    .setDescription(tracksChunk.map((track, index) => `\`${i + index + 1}.\` **[${track.name}](${track.url})** by **${track.artist['#text']}**`).join('\n'));
                embeds.push(embed);
            }

            pagination(session, message, embeds, embeds.length, recentTracks.length, `Recent Tracks for ${lastfmUsername}`, '<:lastfm:1210618435411775549>');
            
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send('An error occurred while fetching most recent tracks.');
        }
    }
};
