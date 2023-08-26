const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const { fetch } = require('undici'), qs = require('qs')

const parse = (str) => {
    const regex = /^([a-zA-Z0-9_ ]{1,16})#([a-zA-Z0-9_]{1,5})$/;
    
    const match = str.match(regex);
  
    if (!match) {
        return false;
    }
  
    const [, username, tagline] = match;
  
    return { username, tagline };
}

module.exports = class Valorant extends Command {
    constructor (bot) {
        super (bot, 'valorant', {
            description : 'Get information on a Valorant player',
            parameters : [ 'username' ],
            syntax : '(username)',
            example : 'alyx#0000',
            aliases : [ 'valo', 'val' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args, prefix) {
        try {
            const { username, tagline } = parse(args.join(' '))

            if (!args[0] || !username || !tagline) {
                return bot.help(
                    message, this, prefix
                )
            }

            const url = `https://tracker.gg/valorant/profile/riot/${encodeURIComponent(`${username}#${tagline}`)}/overview`

            const msg = await bot.neutral(
                message, `Searching for player [\`${username}#${tagline}\`](${url})...`
            )

            const results = await fetch(`https://api.henrikdev.xyz/valorant/v1/account/${username}/${tagline}`, {
                method : 'GET'
            }).then((response) => response.json()).catch((error) => {
                return bot.warn(
                    message, `Bad response (\`${error.response.status}\`) from the **API** (1)`
                )
            })

            if (results.status !== 200) {
                return bot.warn(
                    message, `Could not find player [\`${username}#${tagline}\`](${url})`, {
                        edit : msg
                    }
                )
            }

            const { region, account_level, name, tag, card, last_update_raw } = results.data

            const [ MMR, matches, MMRMatches ] = await Promise.all(
                [
                    fetch(`https://api.henrikdev.xyz/valorant/v1/mmr/${region}/${username}/${tagline}`, {
                        method : 'GET'
                    }).then((response) => response.json()),
                    fetch(`https://api.henrikdev.xyz/valorant/v3/matches/${region}/${username}/${tagline}?filter=competitive`, {
                        method : 'GET'
                    }).then((response) => response.json()),
                    fetch(`https://api.henrikdev.xyz/valorant/v1/mmr-history/${region}/${username}/${tagline}`, {
                        method : 'GET'
                    }).then((response) => response.json())
                ]
            )

            const { currenttierpatched, mmr_change_to_last_game, elo } = MMR.data

            let competitive = []

            if (matches.data.length) {
                competitive = await Promise.all(
                    matches.data.map(async (match, index) => {
                        const { metadata, players, teams } = match

                        const player = players.all_players.find((player) => player.name === name && player.tag === tag)

                        let text = 'Unknown'

                        if (player.team === 'Red') {
                            text = teams.red.has_won ? 'Victory' : 'Defeat'
                        } else if (player.team === 'Blue') {
                            text = teams.blue.has_won ? 'Victory' : 'Defeat'
                        }
                        

                        const mmr = MMRMatches.data[index], change = `(\`${mmr ? `${mmr.mmr_change_to_last_game > 0 ? '+' : ''}${mmr.mmr_change_to_last_game}` : '0'}\`)`

                        return `<t:${metadata.game_start}:d> ${text} ${change}`
                    })
                ) 
            }

            msg.delete()

            message.channel.send({
                embeds : [
                    new Discord.EmbedBuilder({
                        author : {
                            name : message.member.displayName,
                            iconURL : message.member.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        title : `${region.toUpperCase()}: ${name}#${tag}`,
                        url : `https://tracker.gg/valorant/profile/riot/${encodeURIComponent(name)}%23${encodeURIComponent(tag)}/overview`,
                        description : `> **Account Level**: ${account_level}\n> **Rank & ELO**: ${currenttierpatched || 'Unranked'} & ${elo || '0'} (\`${mmr_change_to_last_game >= 0 ? '+' : ''}${mmr_change_to_last_game || '0'}\`)`,
                        fields : competitive.length ? [
                            {
                                name : 'Competitve Matches',
                                value : `> ${competitive.join('\n> ')}`
                            }
                        ] : null,
                        footer : {
                            text : last_update_raw ? 'Last Updated' : null,
                            iconURL : 'https://img.icons8.com/color/512/valorant.png'
                        },
                        thumbnail : {
                            url : card ? card.small : null
                        },
                        timestamp : last_update_raw ? new Date(last_update_raw * 1000) : null
                    }).setColor(bot.colors.neutral)
                ]
            })
        } catch (error) {
            return bot.error(
                message, 'valorant', error
            )
        }
    }
}