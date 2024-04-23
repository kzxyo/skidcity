const https = require('https');
const cheerio = require('cheerio');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'telegram',
        aliases: ['tele'],
        description: 'View a Telegram user\'s information',
        syntax: 'telegram [username]',
        example: 'telegram depression',
        parameters: 'username',
        permissions: 'N/A',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (args.length === 0) {
            return displayCommandInfo(module.exports, session, message);
        }

        const username = args[0];

        try {
            const options = {
                hostname: 't.me',
                port: 443,
                path: `/${username}`,
                method: 'GET'
            };

            const req = https.request(options, res => {
                let html = '';
                res.on('data', chunk => {
                    html += chunk;
                });
                res.on('end', () => {
                    const $ = cheerio.load(html);
                    const metaTags = {};
                    $('meta[property^="og:"]').each((index, element) => {
                        const property = $(element).attr('property').split(':')[1];
                        const content = $(element).attr('content');
                        metaTags[property] = content;
                    });

                    if (metaTags['title'] && metaTags['title'].includes('Telegram: Contact')) {
                        const errorEmbed = new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: That user does not exist`)
                            .setColor(session.warn);
                        message.channel.send({ embeds: [errorEmbed] });
                        return;
                    }

                    const embed = new MessageEmbed()
                        .setTitle(metaTags['title'] || 'Telegram User Profile')
                        .setURL(`https://t.me/${username}`)
                        .setDescription(metaTags['description'] || `You can contact [@${username}](https://t.me/${username}) right away.`)
                        .setThumbnail(metaTags['image'])
                        .setColor('#34ace4')
                        .setFooter(metaTags['site_name'] || 'Telegram', 'https://telegram.org/img/t_logo.png');

                    message.channel.send({ embeds: [embed] });
                });
            });

            req.on('error', error => {
                session.log('Error:', error.message);
                const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
                return message.channel.send({ embeds: [errorEmbed] });
            });

            req.end();
        } catch (error) {
            session.log('Error:', error.message);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
