const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'instagram',
        aliases: ['insta', 'ig'],
        description: 'Get information on an Instagram profile',
        syntax: 'instagram [username]',
        example: 'instagram ye',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        try {
            if (!args.length) {
                return displayCommandInfo(module.exports, session, message);
            }

            const username = args[0];
            const options = {
                method: 'GET',
                url: 'https://instagram-scraper-api2.p.rapidapi.com/v1/info',
                params: {
                    username_or_id_or_url: username
                },
                headers: {
                    'X-RapidAPI-Key': '141e070f61mshebb9f8f7dac8e8fp179694jsnb651b7323525',
                    'X-RapidAPI-Host': 'instagram-scraper-api2.p.rapidapi.com'
                }
            };

            const response = await axios.request(options);
            const userData = response.data.data;

            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`${userData.username}`)
                .setURL(`https://www.instagram.com/${userData.username}`)
                .setDescription(userData.biography || 'No bio available')
                .setThumbnail(userData.profile_pic_url_hd)
                .addField('Followers', userData.follower_count.toLocaleString(), true)
                .addField('Following', userData.following_count.toLocaleString(), true)
                .addField('Posts', userData.media_count.toLocaleString(), true)
                .setFooter('Instagram', 'https://lains.win/instagram.png');

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
