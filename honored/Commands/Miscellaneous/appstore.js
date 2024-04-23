const { MessageEmbed } = require('discord.js');
const AppleStore = require('app-store-scraper');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'appstore',
        aliases: ["playstore", "app"],
        description: 'Search for an app on the App Store.',
        syntax: 'appstore <query>',
        example: 'appstore Uber',
        permissions: 'N/A',
        parameters: 'app',
        module: 'miscellaneous',
        devOnly: true
    },
    run: async (session, message, args) => {
        let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        if (!mentionedMember) mentionedMember = message.member;
        
        if (!args[0]) 
            return displayCommandInfo(module.exports, session, message);

        let img = 'https://cdn4.iconfinder.com/data/icons/miu-black-social-2/60/app_store-512.png';

        AppleStore.search({
            term: args.join(' '),
            num: 1,
        }).then((data) => {
            let AppInfo;

            try {
                AppInfo = JSON.parse(JSON.stringify(data[0]));
            } catch (error) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Couldn't find an app with that name`)
                ]});
            }

            let description = AppInfo.description.length > 200 ? `${AppInfo.description.substr(0, 200)}...` : AppInfo.description;
            let price = AppInfo.free ? 'Free' : `$${AppInfo.price}`;
            let rating = AppInfo.score.toFixed(1);

            const embed = new MessageEmbed()
                .setTitle(`**${AppInfo.title}**`)
                .setThumbnail(AppInfo.icon)
                .setURL(AppInfo.url)
                .setTimestamp()
                .setColor(session.color)
                .setDescription(description)
                .addField(`**Price**`, price, true)
                .addField(`**Developer**`, AppInfo.developer, true)
                .addField(`**Rating**`, rating, true)
                .setFooter(`App Store Results`, img);

            message.channel.send({ embeds: [embed] });
        });
    }
};
