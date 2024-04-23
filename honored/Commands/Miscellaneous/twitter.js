const axios = require('axios');
const { MessageEmbed } = require('discord.js')
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'twitter',
        aliases: ['x'],
        description: 'View a twitter profile',
        syntax: 'twitter [username]',
        example: 'twitter opium',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (!args.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        const screenName = args[0];
        const twitterData = await fetchTwitterData(screenName);

        if (!twitterData) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: Couldn't find a user with the name [\`${screenName}\`](https://x.com/${screenName})`)
            ]});
        }

        const embed = new MessageEmbed()
            .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
            .setColor('#000001')
            .setTitle(`${twitterData.user.name} (@${twitterData.user.profile})`)
            .setURL(`https://twitter.com/${twitterData.user.profile}`)
            .setDescription(twitterData.user.desc || 'No bio available')
            .setThumbnail(twitterData.user.avatar)
            .addField('Posts', twitterData.user.tweet_count.toLocaleString(), true)
            .addField('Following', twitterData.user.friends.toLocaleString(), true)
            .addField('Followers', twitterData.user.sub_count.toLocaleString(), true)
            .setFooter(`X`, 'https://seeklogo.com/images/T/twitter-x-logo-0339F999CF-seeklogo.com.png?v=638264860180000000')

        message.channel.send({ embeds: [embed] });
    }
};

const fetchTwitterData = async (screenName) => {
    const options = {
        method: 'GET',
        url: 'https://twitter-api45.p.rapidapi.com/timeline.php',
        params: {
            screenname: screenName
        },
        headers: {
            'X-RapidAPI-Key': '141e070f61mshebb9f8f7dac8e8fp179694jsnb651b7323525',
            'X-RapidAPI-Host': 'twitter-api45.p.rapidapi.com'
        }
    };

    try {
        const response = await axios.request(options);
        return response.data;
    } catch (error) {
        session.log('Error:', error.message)
        const errorEmbed = new MessageEmbed()
        .setColor(session.warn)
        .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
        return message.channel.send({ embeds: [errorEmbed] });
    }
};
