const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const cheerio = require('cheerio');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'snapchat',
        aliases: ['sc'],
        description: 'Search snapchat for a profile',
        syntax: 'snapchat [username]',
        example: 'snapchat xaviersobased',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        const username = args[0];

        if (!username) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            const response = await axios({
                method: 'GET',
                url: `https://story.snapchat.com/add/${username}`
            });

            if (response.status !== 200) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: Couldn't find the username [\`${username}\`](https://snapchat.com/add/${username})`)
                    ]
                });
            }

            const $ = cheerio.load(response.data);
            const scriptData = $('script#__NEXT_DATA__').html();
            const json = JSON.parse(scriptData);

            const user = json.props.pageProps.userProfile;
            const public = user.publicProfileInfo || user.userInfo;

            const embed = new MessageEmbed()
                .setColor('#FFFC00')
                .setTitle(`${public.displayName || public.title || public.username} (@${username})`)
                .setURL(`https://www.snapchat.com/add/${public.username}`)
                .setImage(public.snapcodeImageUrl.replace('SVG', 'PNG'));

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
