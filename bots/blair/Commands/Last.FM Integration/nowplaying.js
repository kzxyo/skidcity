const Command = require('../../Structures/Base/Command.js')

const { EmbedBuilder } = require('discord.js')
const Phin = require('phin')

module.exports = class NowPlaying extends Command {
    constructor (Client) {
        super (Client, 'nowplaying', {
            Aliases : [ 'np', 'fm', 'now' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        var UpvoteReaction = '🔥', DownvoteReaction = '🗑️'
        Message.channel.sendTyping()

        try {
            const Member = await Arguments[0] ? Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(Member => String(Member.user.username).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(Member.user.tag).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(Member.displayName).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase())) || Message.mentions.members.last() : Message.member
            if (!Member) {
                return new Client.Response(
                    Message, `Couldn't find a **Member** with the username: **${Arguments.join(' ')}**.`
                )
            }

            Client.Database.query(`SELECT * FROM lastfms WHERE user_id = ${Member.id}`).then(async ([Results]) => {
                if (Results.length === 0) {
                    return new Client.Response(
                        Message, Member === Message.member ? `You haven't set your **Last.FM** username - Connect it with \`lastfm set (Username)\`` : `Member **${Member.user.tag}** does not have their **Last.FM** username set.`
                    )
                }

                const RecentTracks = await Phin({
                    url : `http://ws.audioscrobbler.com/2.0/?api_key=${process.env.LastFM}&method=user.getrecenttracks&user=${Results[0].username}&limit=1&format=json`,
                    method : 'GET',
                    parse : 'json'
                })

                if (RecentTracks.status == 404) {
                    return new Client.Response(
                        Message, Member === Message.member ? `You dont have any **Recent Tracks** on **Last.FM**.` : `Member **${Member.user.tag}** does not have any **Recent Tracks** on **Last.FM**.`
                    )
                }

                const Track = RecentTracks.body.recenttracks.track[0]

                if (!Track) {
                    return new Client.Embed(
                        Message, `Couldn't find that **Track** on **Last.FM**.`
                    )
                }

                const Artist = Track.artist['#text']
                const Album = Track.album['#text' || 'N/A']
                
                const ArtistURL = "https://www.last.fm/music/" + `${Artist.replace(/ /g, '+')}`
                const AlbumURL = "https://www.last.fm/music/" + `${Artist.replace(/ /g, '+')}/` + `${Album.replace(/ /g, '+')}`
                
                const Scrobbles = parseInt(RecentTracks.body.recenttracks['@attr'].total).toLocaleString()

                const TrackInformation = await Phin({
                    url : `http://ws.audioscrobbler.com/2.0/?api_key=${process.env.LastFM}&method=track.getinfo&username=${Results[0].username}&track=${Track.name}&artist=${Artist}&format=json&autocorrect=true`,
                    method : 'GET',
                    parse : 'json'
                })

                var Plays, TrackData, Status = 'Most Recent'
                
                if (RecentTracks.body.recenttracks.track[0]['@attr']) Status = 'Now Playing'
                if (TrackInformation) TrackData = TrackInformation.body.track
                                
                if (!TrackData) Plays = '0'
                if (TrackData) Plays = parseInt(TrackData.userplaycount).toLocaleString()

                const UserInformation = await Phin({
                    url : `http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=${Results[0].username}&api_key=${process.env.LastFM}&format=json`,
                    method : 'GET',
                    parse : 'json'
                })

                Client.Database.query('SELECT * FROM lastfm_modes WHERE user_id = $1', { bind : [Message.author.id] }).then(async ([Results2]) => {
                    if (Member !== Message.member || Results2.length === 0) {
                        Message.channel.send({
                            embeds : [
                                new EmbedBuilder({
                                    author : {
                                        name : `Last.FM: ${Results[0].username}`,
                                        iconURL : UserInformation.body.user.image[3]['#text'].replace('.png', '.gif') || Member.displayAvatarURL({
                                            dynamic : true
                                        }),
                                        url : `https://www.last.fm/user/${Results[0].username}`
                                    },
                                    fields : [
                                        {
                                            name : 'Track',
                                            value : `[${Track.name}](${Track.url})`,
                                            inline : true
                                        },
                                        {
                                            name : 'Artist',
                                            value : `[${Artist}](${ArtistURL})`,
                                            inline : true
                                        }
                                    ],
                                    footer : {
                                        text : `${Plays} plays out of ${Scrobbles} scrobbles ∙ Album: ${Album}`
                                    }
                                }).setColor(Client.Color).setThumbnail(Track.image[3]['#text'])
                            ]
                        }).then(async (x) => {
                            x.react(UpvoteReaction)
                            x.react(DownvoteReaction)
                        })
                    } else {
                        const Embed = new Client.EmbedParser(Results2[0].embed)
                        
                        Message.channel.send(Embed).then(async (x) => {
                            x.react(UpvoteReaction)
                            x.react(DownvoteReaction)
                        }).catch((Error) => {
                            return new Client.Response(
                                Message, `Error occurred while using custom **Now Playing** embed.\n\`\`\`${Error.message}\`\`\``
                            )
                        })
                    }
                })
            })
        } catch (Error) {
            return new Client.Error(
                Message, 'nowplaying', Error
            )
        }
    }
}