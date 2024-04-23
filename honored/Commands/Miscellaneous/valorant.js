const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'valorant',
        aliases: ['val'],
        description: 'Get information on a Valorant profile',
        syntax: 'valorant [username]',
        example: 'valorant carter#swag',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args, prefix) => {
        const parse = (str) => {
            const regex = /^([a-zA-Z0-9_ ]{1,16})#([a-zA-Z0-9_]{1,5})$/;
            const match = str.match(regex);

            if (!match) {
                return false;
            }

            const [, username, tagline] = match;
            return { username, tagline };
        };

        try {
            const { username, tagline } = parse(args.join(' '));

            if (!args[0] || !username || !tagline) {
                return displayCommandInfo(module.exports, session, message, prefix);
            }

            const url = `https://tracker.gg/valorant/profile/riot/${encodeURIComponent(`${username}#${tagline}`)}/overview`;

            const embedSearching = new MessageEmbed()
                .setColor(session.color)
                .setDescription(`> Searching for player [\`${username}#${tagline}\`](${url})...`);
            const msg = await message.channel.send({ embeds: [embedSearching] });

            const response = await axios.get(`https://api.henrikdev.xyz/valorant/v1/account/${username}/${tagline}`);
            const results = response.data;

            if (response.status !== 200) {
                const embedError = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Could not find player [\`${username}#${tagline}\`](${url})`);

                return message.channel.send({ embeds: [embedError] });
            }

            const { region, account_level, name, tag, card, last_update_raw } = results.data;

            const [MMR, matches, MMRMatches] = await Promise.all(
                [
                    fetch(`https://api.henrikdev.xyz/valorant/v1/mmr/${region}/${username}/${tagline}`, {
                        method: 'GET'
                    }).then((response) => response.json()),
                    fetch(`https://api.henrikdev.xyz/valorant/v3/matches/${region}/${username}/${tagline}?filter=competitive`, {
                        method: 'GET'
                    }).then((response) => response.json()),
                    fetch(`https://api.henrikdev.xyz/valorant/v1/mmr-history/${region}/${username}/${tagline}`, {
                        method: 'GET'
                    }).then((response) => response.json())
                ]
            );

            const { currenttierpatched, mmr_change_to_last_game, elo } = MMR.data;

            let competitive = [];

            if (matches.data.length) {
                competitive = await Promise.all(
                    matches.data.map(async (match, index) => {
                        const { metadata, players, teams } = match;

                        const player = players.all_players.find((player) => player.name === name && player.tag === tag);

                        let text = 'Unknown';

                        if (player.team === 'Red') {
                            text = teams.red.has_won ? 'Victory' : 'Defeat';
                        } else if (player.team === 'Blue') {
                            text = teams.blue.has_won ? 'Victory' : 'Defeat';
                        }

                        const mmr = MMRMatches.data[index];
                        const change = `(\`${mmr ? `${mmr.mmr_change_to_last_game > 0 ? '+' : ''}${mmr.mmr_change_to_last_game}` : '0'}\`)`;

                        return `**${new Date(metadata.game_start * 1000).toLocaleDateString()}**: ${text} ${change}`;
                    })
                );
            }

            const embedResults = new MessageEmbed()
                .setColor('#fc4c5c')
                .setTitle(`${region.toUpperCase()}: ${name}#${tag}`)
                .setURL(`https://tracker.gg/valorant/profile/riot/${encodeURIComponent(name)}%23${encodeURIComponent(tag)}/overview`)
                .setDescription(`**Account Level:** ${account_level}\n**Rank & ELO:** ${currenttierpatched || 'Unranked'} & ${elo || '0'} (\`${mmr_change_to_last_game >= 0 ? '+' : ''}${mmr_change_to_last_game || '0'}\`)`)
                .setFooter('Valorant', 'https://cdn.discordapp.com/attachments/1209568138514006077/1209568146952814692/1664302686valorant-icon-png.png?ex=65e7651e&is=65d4f01e&hm=4869a0e706b6a8947100832df056a2ef9c22e9b3a9bff94d06ad2e91fc368479&')

            if (card) {
                embedResults.setThumbnail(card.small);
            }

            msg.delete();
            message.channel.send({ embeds: [embedResults] });
        } catch (error) {
            session.log('Error:', error.message);

            const embedError = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: API returned an errorr`);

            message.channel.send({ embeds: [embedError] });
        }
    }
};
