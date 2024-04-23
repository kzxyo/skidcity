const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const filePath = '/root/rewrite/Database/lastfm.json';

module.exports = {
    configuration: {
        commandName: 'nowplaying',
        aliases: ['fm', 'np'],
        description: 'Shows your most recent track',
        syntax: 'nowplaying',
        example: 'nowplaying',
        module: 'lastfm'
    },
    run: async (session, message, args) => {
        const key = session.lastfmkey;
        const lastfmData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const mentionedUser = message.mentions.users.first();

        let userID;
        if (mentionedUser) {
            userID = mentionedUser.id;
        } else {
            userID = message.author.id;
        }

        const lastfmUsername = lastfmData[userID];
        if (!lastfmUsername) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor('#FF0000')
                    .setDescription(`<:lastfm:1210618435411775549> ${message.author}: One of you dont have a LastFM username set. run \`lastfm set [username]\` to set one`)
            ]});
        }

        try {
            const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=${lastfmUsername}&api_key=${key}&format=json&limit=1`);
            const recentTrack = data.recenttracks.track[0];

            if (!recentTrack) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`<:lastfm:1210618435411775549> ${mentionedUser}: ${mentionedUser.id === message.author.id ? "You don't have" : "This user doesn't have"} a LastFM username set. run \`lastfm set [username]\` to set one`)
                ]});
            }

            const avatarURL = `https://www.last.fm/user/${lastfmUsername}/`;
            
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(`Last.fm: ${lastfmUsername}`, avatarURL)
                .addField('Track', `[${recentTrack.name}](https://discord.gg/okay)`, true)
                .addField('Artist', `[${recentTrack.artist['#text']}](https://discord.gg/okay)`, true)
                .setThumbnail(recentTrack.image[2]['#text'])
            
            return message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send('An error occurred while fetching most recent track.');
        }
    }
};
