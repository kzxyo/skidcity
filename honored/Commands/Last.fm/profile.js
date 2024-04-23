const { MessageEmbed } = require("discord.js");
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'profile',
        aliases: ['pf'],
        description: 'View a Last.fm profile',
        syntax: 'profile [username]',
        example: 'profile twix',
        permissions: 'N/A',
        parameters: 'username',
        module: 'lastfm'
    },
    run: async (session, message, args) => {

        if (args.length === 0) {
            return displayCommandInfo(module.exports, session, message);
        }

        const username = args[0];

        try {
            const response = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=${username}&api_key=${session.lastfmkey}&format=json`);
            const userData = response.data.user;
            
            const embed = new MessageEmbed()
                .setTitle(`Last.FM: ${username}`)
                .setURL(`https://www.last.fm/user/${username}`)
                .setThumbnail(userData.image[2]['#text'])
                .setDescription(`**Registered:** ${new Date(userData.registered.unixtime * 1000).toLocaleDateString()}\n**Country:** ${userData.country || 'N/A'}`)
                .addField('Statistics', `**Playcount:** ${userData.playcount.toLocaleString()}\n**Scrobbles:** ${userData.playcount.toLocaleString()}\n**Albums:** ${userData.album_count.toLocaleString()}\n**Tracks:** ${userData.track_count.toLocaleString()}`)
                .setColor(session.color)


            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error fetching Last.fm profile:', error.message);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                    .setColor('#ff0000')
                    .setDescription(`Error fetching Last.fm profile for ${username}`)
                ]
            });
        }
    }
};
