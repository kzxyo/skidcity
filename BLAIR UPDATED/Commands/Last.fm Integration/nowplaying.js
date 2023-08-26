const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const { fetch } = require('undici')

module.exports = class NowPlaying extends Command {
    constructor (bot) {
        super (bot, 'nowplaying', {
            description : 'Show your current song on Last.fm',
            parameters : [ 'member' ],
            syntax : '<member>',
            example : bot.owner.username,
            aliases : [ 'np', 'now', 'fm' ],
            module : 'Last.fm Integration'
        })
    }

    async execute (bot, message, args, prefix) {
        try {
            message.channel.sendTyping()

            const member = message.member

            const [ data ] = await Promise.all(
                [
                    bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                        bind : [
                            member.user.id
                        ]
                    }).then(([results]) => results[0])
                ]
            )

            if (!data) {
                const operator = member === message.member ? `You haven't set your **Last.fm** username - \`${message.prefix}lastfm set (username)\`` : `**${member.tag}** hasn't set their **Last.fm** username`

                return bot.warn(
                    message, operator
                )
            }

            const [ recent, user ] = await Promise.all(
                [
                    fetch(`http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=${data.username}&api_key=${process.env.LASTFM_API_KEY}&format=json`, {
                        method : 'GET'
                    }).then((results) => results.json()),
                    fetch(`http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=${data.username}&api_key=${process.env.LASTFM_API_KEY}&format=json`, {
                        method : 'GET'
                    }).then((results) => results.json())
                ]
            )

            if (!recent.recenttracks.track.length) {
                const operator = member === message.member ? `Could not fetch your **most recent track**` : `Could not fetch **${member.user.tag}**'s **most recent track**`

                return bot.warn(
                    message, operator
                )
            }

            if (!user) {
                return bot.warn(
                    message, `Could not fetch the **Last.fm profile**`
                )
            }

            const track = recent.recenttracks.track[0], artist = { name : track.artist['#text'], url : 'https://last.fm/music/' + track.artist['#text'].replace(/ /g, '+') }, album = track.album['#text' || 'None']

            const scrobbles = parseInt(recent.recenttracks['@attr'].total).toLocaleString()

            const information = await fetch(`http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=${process.env.LASTFM_API_KEY}&artist=${artist.name}&track=${track.name}&user=${data.username}&format=json`, {
                method : 'GET'
            }).then((results) => results.json()).catch(() => {})

            let plays, t

            if (information) t = information.track
            plays = t ? parseInt(t.userplaycount).toLocaleString() : '0'

            const avatar = user.user.image[3]['#text'].replace('.png', '.gif') || member.displayAvatarURL({ dynamic : true })

            let msg

            msg = await message.channel.send({
                embeds : [
                    new Discord.EmbedBuilder({
                        author : {
                            name : `Last.fm: ${user.user.name}`,
                            iconURL : avatar,
                            url : user.user.url
                        },
                        fields : [
                            {
                                name : 'Track',
                                value : `[${track.name}](${track.url})`,
                                inline : true
                            },
                            {
                                name : 'Artist',
                                value : `[${artist.name}](${artist.url})`,
                                inline : true
                            }
                        ],
                        footer : {
                            text : `Plays: ${plays} ∙ Scrobbles: ${scrobbles} ∙ Album: ${album}`
                        },
                        thumbnail : {
                            url : track.image[3]['#text']
                        }
                    }).setColor(bot.colors.neutral)
                ]
            })

            let upvote = '👍', downvote = '👎'

            msg.react(upvote)
            msg.react(downvote)
        } catch (error) {
            return bot.error(
                message, 'nowplaying', error
            )
        }
    }
}