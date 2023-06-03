const Commands = [ 'set', 'link', 'connect', 'mode', 'embed' ]
const { EmbedBuilder, ActionRowBuilder, ButtonBuilder } = require('discord.js')

const Command = require('../../Structures/Base/Command.js')

const Phin = require('phin')

module.exports = class LastFM extends Command {
    constructor (Client) {
        super (Client, 'lastfm', {
            Aliases : [ 'lf', 'lfm' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            return new Client.Response(
                Message, `You can view available **Last.FM** commands on the [Commands](https://blair.win/commands) page.`
            )
        }

        switch (Command) {
            case (Command === 'set' ? Command : Command === 'link' ? Command : Command === 'connect' ? Command : '') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            About : 'Set your Last.FM username for access to commands.',
                            Syntax : 'lastfm set (Username)'
                        }
                    )
                }

                try {
                    if (String(Arguments[1]).toLowerCase() === 'none') {
                        Client.Database.query(`SELECT * FROM lastfms WHERE user_id = ${Message.author.id}`).then(async ([Results]) => {
                            if (Results.length === 0) {
                                return new Client.Response(
                                    Message, `You haven't set a **Last.FM** username to remove.`
                                )
                            }

                            Client.Database.query(`DELETE FROM lastfms WHERE user_id = ${Message.author.id}`).then(() => {
                                return new Client.Response(
                                    Message, `Your **Last.FM** username has been removed.`
                                )
                            }).catch((Error) => {
                                console.error(Error)
                            })
                        })
                    } else {
                        const Username = String(Arguments[1]).toLowerCase()

                        const Account = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?api_key=${process.env.LastFM}&method=user.getInfo&format=json&user=${Username}`,
                            method : 'GET',
                            parse : 'json'
                        }).catch(() => {})

                        if (Account.body.message === 'User not found') {
                            return new Client.Response(
                                Message, `Couldn't find a **Last.FM** account with that username.`
                            )
                        }

                        Client.Database.query(`SELECT * FROM lastfms WHERE user_id = ${Message.author.id}`).then(([Results]) => {
                            if (Results.length > 0) {
                                Client.Database.query(`UPDATE lastfms SET username = '${Username}' WHERE user_id = ${Message.author.id}`).then(() => {
                                    return new Client.Response(
                                        Message, `Your **Last.FM** username has been updated as [**${Username}**](https://last.fm/user/${Username}).`
                                    )
                                }).catch((Error) => {
                                    console.error(Error)
                                })
                            } else {
                                Client.Database.query(`INSERT INTO lastfms (user_id, username) VALUES (${Message.author.id}, '${Username}')`).then(() => {
                                    return new Client.Response(
                                        Message, `Your **Last.FM** username has been set as [**${Username}**](https://last.fm/user/${Username}).`
                                    )
                                }).catch((Error) => {
                                    console.error(Error)
                                })
                            }
                        }) 
                    }
                } catch (Error) {
                    return new Client.Error(
                        Message, `lastfm set`, Error
                    )
                }

                break
            }

            case (Command === 'mode' ? Command : Command === 'embed' ? Command : '') : {
                const Command = String(Arguments[1]).toLowerCase()
                const Commands = [ 'check', 'default' ]

                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {

                        }
                    )
                }

                if (Commands.includes(Command)) {
                    switch (Command) {
                        case ('check') : {
                            Client.Database.query('SELECT * FROM lastfm_modes WHERE user_id = $1', { bind : [ Message.author.id ] }).then(async ([Results]) => {
                                try {
                                    if (Results.length === 0) {
                                        return new Client.Response(
                                            Message, `You haven't set a custom **Now Playing** embed.`
                                        )
                                    }

                                    if (Arguments.includes('-mobile')) {
                                        Message.channel.send(`${Results[0].embed}`)
                                    } else {
                                        new Client.Response(
                                            Message, `\`\`\`${Results[0].embed}\`\`\``
                                        )
                                    }
                                } catch (Error) {
                                    return new Client.Error(
                                        Message, 'lastfm mode check', Error
                                    )
                                }
                            })

                            break
                        }

                        case ('default') : {
                            Client.Database.query('SELECT * FROM lastfm_modes WHERE user_id = $1', { bind : [ Message.author.id ] }).then(async ([Results]) => {
                                try {
                                    if (Results.length === 0) {
                                        return new Client.Response(
                                            Message, `You haven't set a custom **Now Playing** embed.`
                                        )
                                    }

                                    Client.Database.query('DELETE FROM lastfm_modes WHERE user_id = $1', {
                                        bind : [ Message.author.id ]
                                    })

                                    new Client.Response(
                                        Message, `Set your **Now Playing** embed back to default.`
                                    )
                                } catch (Error) {
                                    return new Client.Error(
                                        Message, 'lastfm mode default', Error
                                    )
                                }
                            })

                            break
                        }
                    }
                } else {
                    const EmbedCode = Arguments.slice(1).join(' ')

                    Client.Database.query('SELECT * FROM lastfm_modes WHERE user_id = $1', { bind : [ Message.author.id ] }).then(async ([Results]) => {
                        try {
                            if (Results.length === 0) {
                                Client.Database.query('INSERT INTO lastfm_modes (user_id, embed) VALUES ($1, $2)', {
                                    bind : [ Message.author.id, EmbedCode ]
                                })
                            } else {
                                Client.Database.query('UPDATE lastfm_modes SET embed = $1 WHERE user_id = $2', {
                                    bind : [ EmbedCode, Message.author.id ]
                                })
                            }
                            
                            new Client.Response(
                                Message, `Set your custom **Now Playing** embed.\n\`\`\`${EmbedCode}\`\`\``
                            )
                        } catch (Error) {
                            return new Client.Error(
                                Message, 'lastfm mode', Error
                            )
                        }
                    })
                }

                break
            }

            case (Command === 'profile' ? Command : Command === 'whois' ? Command : '') : {
                Message.channel.sendTyping()

                try {
                    const Member = await Arguments[1] ? Message.guild.members.cache.get(Arguments[1]) || Message.guild.members.cache.find(Member => String(Member.user.username).toLowerCase().includes(String(Arguments.slice(1).join(' ')).toLowerCase()) || String(Member.user.tag).toLowerCase().includes(String(Arguments.slice(1).join(' ')).toLowerCase()) || String(Member.displayName).toLowerCase().includes(String(Arguments.slice(1).join(' ')).toLowerCase())) || Message.mentions.members.last() : Message.member

                    if (!Member) {
                        return new Client.Response(
                            Message, `Couldn't find a **Member** with the username: **${Arguments.join(' ')}**.`
                        )
                    }

                    Client.Database.query(`SELECT * FROM lastfms WHERE user_id = ${Member.id}`).then(async ([Results]) => {
                        if (Results.length === 0) {
                            return new Client.Response(
                                Message, Member === Message.member ? `You haven't set your **Last.FM** username.` : `Member **${Member.user.tag}** does not have their **Last.FM** username set.`
                            )
                        }

                        const UserInformation = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=${Results[0].username}&api_key=${process.env.LastFM}&format=json`,
                            method : 'GET',
                            parse : 'json'
                        })

                        const TopArtists = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=${Results[0].username}&api_key=${process.env.LastFM}&format=json&limit=1`,
                            method : 'GET',
                            parse : 'json'
                        })
                        
                        const TopTracks = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=${Results[0].username}&api_key=${process.env.LastFM}&format=json&limit=1`,
                            method : 'GET',
                            parse : 'json'
                        })

                        const TopAlbums = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=${Results[0].username}&api_key=${process.env.LastFM}&format=json&limit=1`,
                            method : 'GET',
                            parse : 'json'
                        })

                        const RecentTracks = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?api_key=${process.env.LastFM}&method=user.getrecenttracks&user=${Results[0].username}&limit=1&format=json`,
                            method : 'GET',
                            parse : 'json'
                        })

                        const Track = RecentTracks.body.recenttracks.track[0]

                        const Artist = Track.artist['#text']
                        const ArtistURL = "https://www.last.fm/music/" + `${Artist.replace(/ /g, '+')}`

                        Message.channel.send({
                            embeds : [
                                new EmbedBuilder({
                                    author : {
                                        name : String(Message.member.displayName),
                                        iconURL : Message.member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    },
                                    title : `${UserInformation.body.user.realname ? `${UserInformation.body.user.realname} (${UserInformation.body.user.name})` : UserInformation.body.user.name}`,
                                    url : `https://last.fm/user/${UserInformation.body.user.name}`,
                                    description : `${RecentTracks.body.recenttracks.track[0]['@attr'] ? `Currently listening to:` : `Last Listened to:`} [${Track.name}](${Track.url}) by [${Artist}](${ArtistURL})`,
                                    fields : [
                                        {
                                            name : 'Country',
                                            value : `${UserInformation.body.user.country}`,
                                            inline : true
                                        },
                                        {
                                            name : 'Scrobbles',
                                            value : `${parseInt(UserInformation.body.user.playcount).toLocaleString()}`,
                                            inline : true
                                        },
                                        {
                                            name : 'Registered',
                                            value : `<t:${UserInformation.body.user.registered.unixtime}:D>`,
                                            inline : true
                                        },
                                        {
                                            name : `Top Artist (${parseInt(TopArtists.body.topartists.artist[0].playcount).toLocaleString()})`,
                                            value : `[${TopArtists.body.topartists.artist[0].name}](${TopArtists.body.topartists.artist[0].url})`,
                                            inline : true
                                        },
                                        {
                                            name : `Top Track (${parseInt(TopTracks.body.toptracks.track[0].playcount).toLocaleString()})`,
                                            value : `[${TopTracks.body.toptracks.track[0].name}](${TopTracks.body.toptracks.track[0].url})`,
                                            inline : true
                                        },
                                        {
                                            name : `Top Album (${parseInt(TopAlbums.body.topalbums.album[0].playcount).toLocaleString()})`,
                                            value : `[${TopAlbums.body.topalbums.album[0].name}](${TopAlbums.body.topalbums.album[0].url})`,
                                            inline : true
                                        }
                                    ],
                                    thumbnail : {
                                        url : UserInformation.body.user.image[3]['#text'] || Member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    }
                                }).setColor(Client.Color)
                            ]
                        })
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'lastfm profile', Error
                    )
                }

                break
            }

            case (Command === 'inspect' ? Command : Command === 'check' ? Command : '') : {
                if (Client.Staff.includes(Message.author.id)) {
                    if (!Arguments[1]) {
                        return new Client.Help(
                            Message, {
                                About : 'Check every account with the given Last.FM username set.',
                                Syntax : 'lastfm inspect (Username)'
                            }
                        )
                    }

                    try {
                        const Username = String(Arguments[1]).toLowerCase()

                        const Account = await Phin({
                            url : `http://ws.audioscrobbler.com/2.0/?api_key=${process.env.LastFM}&method=user.getInfo&format=json&user=${Username}`,
                            method : 'GET',
                            parse : 'json'
                        }).catch(() => {})

                        if (Account.body.message === 'User not found') {
                            return new Client.Response(
                                Message, `Couldn't find a **Last.FM** account with that username.`
                            )
                        }

                        Client.Database.query(`SELECT * FROM lastfms WHERE username = '${Username}'`).then(async ([Results]) => {
                            if (Results.length === 0) {
                                return new Client.Response(
                                    Message, `Couldn't find any **Users** with that username set.`
                                )
                            }

                            const Users = []

                            for (const Result of Results) {
                                const User = await Client.users.fetch(Client.users.resolveId(Result.user_id)).catch(() => {})

                                Users.push(User)
                            }

                            const Embeds = [], Pager = Users.Pager(10); var Index = 0

                            for (const Entry of Pager) {
                                const Mapped = Entry.map((Item) => {
                                    return `\`${++Index}\` **${Item.tag}** (*${Item.id}*)` 
                                }).join('\n')
                                
                                Embeds.push(new EmbedBuilder({
                                    author : {
                                        name : String(Message.member.displayName),
                                        iconURL : Message.member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    },
                                    title : `Inspecting: ${Username}`,
                                    url : `https://last.fm/user/${Username}`,
                                    description : Mapped,
                                    footer : {
                                        text : `Page 1/1 (${Index} ${Index === 1 ? 'entry' : 'entries'})`
                                    }
                                }).setColor(Client.Color))
                            }

                            Message.channel.send({
                                embeds : [
                                    Embeds[0]
                                ]
                            })
                        })
                    } catch (Error) {
                        return new Client.Error(
                            Message, 'lastfm inspect', Error
                        )
                    }
                }
            }
        }
    }
}

class Library {
    constructor (Username, Member) {

    }

    async Start () {

    }

    async GetArtist () {

    }

    async Next () {

    }
}