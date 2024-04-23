const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'github',
        description: 'View a github profile',
        syntax: 'github [username]',
        example: 'github egirl',
        permissions: 'N/A',
        parameters: 'username',
        aliases: ['git', 'gh'],
        module: 'miscellaneous'
    },

    run: async (session, message, args) => {
        try {
            const username = args[0];
            if (!username) {
                return displayCommandInfo(module.exports, session, message);
            }

            const response = await axios.get(`https://api.github.com/users/${username}`);
            const data = response.data;

            if (response.status === 404) {
                const errorEmbed = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} **${username}** is an invalid **Github** account`);
                return message.channel.send({ embeds: [errorEmbed] });
            }

            const embed = new MessageEmbed()
                .setColor('#748cdc')
                .setTitle(data.name ? `${data.name} (@${data.login})` : data.login)
                .setURL(data.html_url)
                .setTimestamp(new Date(data.created_at))
                .setThumbnail(data.avatar_url);

            let information = (data.bio || '') +
                (data.email ? `\n📧 ${data.email}` : '') +
                (data.company ? `\n🏢 [${data.company}](https://google.com/search?q=${encodeURIComponent(data.company)})` : '') +
                (data.location ? `\n🌎 [${data.location}](https://maps.google.com/search?q=${encodeURIComponent(data.location)})` : '') +
                (data.twitter_username ? `\n<:twitter:1195575740863873125> [${data.twitter_username}](https://twitter.com/${data.twitter_username})` : '');

            if (information) {
                embed.addField('Information', information, false);
            }

            if (data.public_repos) {
                const reposResponse = await axios.get(data.repos_url);
                const repos = reposResponse.data;

                embed.addField(`Repositories (${repos.length})`, repos
                    .sort((a, b) => b.stargazers_count - a.stargazers_count)
                    .slice(0, 3)
                    .map(repo => `[⭐ ${repo.stargazers_count.toLocaleString()}, ${new Date(repo.created_at).toLocaleDateString('en-US')} ${repo.name}](${repo.html_url})`)
                    .join('\n'), false);
            }

            embed.addFields(
                { name: 'Following', value: data.following.toLocaleString(), inline: true },
                { name: 'Followers', value: data.followers.toLocaleString(), inline: true },
                { name: 'Public Repos', value: data.public_repos.toLocaleString(), inline: true }
            );

            embed.setFooter('Created on', 'https://cdn.discordapp.com/emojis/843537056541442068.png');

            return message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
