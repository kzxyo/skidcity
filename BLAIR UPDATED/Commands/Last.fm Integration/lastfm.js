const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const error = (member, author, type) => {
    if (member.id === author.id) {
        switch (type) {
            case ('notConnected') : {
                return `You have not set your **Last.fm** username - \`lastfm set (username)\``
            }

            case ('noRecentTracks') : {
                return `You don't have any **recent tracks**.`
            }
        }
    } else {
        switch (type) {
            case ('notConnected') : {
                return `**${member.tag}** has not set their **Last.fm** username.`
            }

            case ('noRecentTracks') : {
                return `**${member.tag}** does not have any **recent tracks**.`
            }
        }
    }
}

const commands = {
    general : [
        'set', 'link', 'connect',
        'mode', 'embed',
        'reactions', 'reaction', 'react', 'cr'
    ],
    username : [
        'update', 'refresh', 'reload', 'index',
        'whoknows', 'wk',
        'wkalbum', 'whoknowsalbum', 'wka',
        'wktrack', 'whoknowstrack', 'wkt',
        'globalwhoknows', 'globalwk', 'gwk',
        'globalwkalbum', 'globalwka', 'gwka',
        'globalwktrack', 'globalwkt', 'gwkt',
        'topartists', 'topartist', 'artists', 'artist', 'tar', 'ta',
        'topalbums', 'topalbum', 'albums', 'album', 'tab', 'tl',
        'toptracks', 'toptrack', 'tracks', 'track', 'ttr', 'tt',
        'plays',
        'playsalbum', 'playsa', 'aplays',
        'playstrack', 'playst', 'tplays',
        'compare', 'taste', 'mutual', 'match'
    ]
}, allCommands = [ ...commands.general, ...commands.username ]

const axios = require('axios'), sequelize = require('sequelize'), { fetch } = require('undici')

module.exports = class LastFM extends Command {
    constructor (bot) {
        super (
            bot, 'lastfm', {
                description : 'All commands to interact with the Last.fm website.',
                parameters : [ 'command', 'arguments' ],
                syntax : '(command) <arguments>',
                example : 'set imissher',
                aliases : [ 'lf', 'lfm' ],
                commands : [
                    {
                        name : 'lastfm set',
                        description : 'Set your Last.fm username.',
                        parameters : [ 'username' ],
                        syntax : '(username)',
                        example : 'imissher',
                        aliases :  [ 'link', 'connect' ]
                    },
                    {
                        name : 'lastfm update',
                        description : 'Index your Last.fm library.',
                        aliases : [ 'refresh', 'reload', 'index' ]
                    },
                    {
                        name : 'lastfm mode',
                        description : 'Set a custom Now Playing embed.',
                        parameters : [ 'mode' ],
                        syntax : '(embed code)',
                        example : '{embed: $title: Hi}',
                        aliases : [ 'embed' ]
                    },
                    {
                        name : 'lastfm reactions',
                        description : 'Set custom Now Playing reactions.',
                        parameters : [ 'upvote', 'downvote' ],
                        syntax : '(upvote) (downvote)',
                        example : '🔥 🗑️',
                        aliases : [ 'reaction', 'react', 'cr' ]
                    },
                    {
                        name : 'lastfm whoknows',
                        description : 'Show the top listeners for an artist.',
                        parameters : [ 'artist' ],
                        syntax : '<artist>',
                        example : 'Destroy Lonely',
                        aliases : [ 'wk' ]
                    },
                    {
                        name : 'lastfm wkalbum',
                        description : 'Show the top listeners for an album.',
                        parameters : [ 'album' ],
                        syntax : '<album>',
                        example : 'Darkhorse',
                        aliases : [ 'whoknowsalbum', 'wka' ]
                    },
                    {
                        name : 'lastfm wktrack',
                        description : 'Show the top listeners for a track.',
                        parameters : [ 'track' ],
                        syntax : '<track>',
                        example : '4seasons',
                        aliases : [ 'whoknowstrack', 'wkt' ]
                    },
                    {
                        name : 'lastfm globalwhoknows',
                        description : 'Show the top global listeners for an artist.',
                        parameters : [ 'artist' ],
                        syntax : '<artist>',
                        example : 'Destroy Lonely',
                        aliases : [ 'globalwk', 'gwk' ]
                    },
                    {
                        name : 'lastfm globalwkalbum',
                        description : 'Show the top global listeners for an album.',
                        parameters : [ 'album' ],
                        syntax : '<album>',
                        example : 'Darkhorse',
                        aliases : [ 'globalwka', 'gwka' ]
                    },
                    {
                        name : 'lastfm globalwktrack',
                        description : 'Show the top global listeners for a track.',
                        parameters : [ 'track' ],
                        syntax : '<track>',
                        example : '4seasons',
                        aliases : [ 'globalwkt', 'gwkt' ]
                    },
                    {
                        name : 'lastfm topartists',
                        description : 'Show the top artists of yourself or someone else.',
                        parameters : [ 'member', 'period' ],
                        syntax : '<member> <period>',
                        example : `${bot.owner.username} 7d`,
                        aliases : [ 'topartist', 'artists', 'artist', 'tar', 'ta' ]
                    },
                    {
                        name : 'lastfm topalbums',
                        description : 'Show the top albums of yourself or someone else.',
                        parameters : [ 'member', 'period' ],
                        syntax : '<member> <period>',
                        example : `${bot.owner.username} 7d`,
                        aliases : [ 'topalbum', 'albums', 'album', 'tab', 'tl' ]
                    },
                    {
                        name : 'lastfm toptracks',
                        description : 'Show the top tracks of yourself or someone else.',
                        parameters : [ 'member', 'period' ],
                        syntax : '<member> <period>',
                        example : `${bot.owner.username} 7d`,
                        aliases : [ 'toptrack', 'tracks', 'track', 'ttr', 'tt' ]
                    },
                    {
                        name : 'lastfm plays',
                        description : 'Show your plays for an artist.',
                        parameters : [ 'member', 'artist' ],
                        syntax : '<member> <artist>',
                        example : `${bot.owner.username} Destroy Lonely`
                    },
                    {
                        name : 'lastfm playsalbum',
                        description : 'Show your plays for an album.',
                        parameters : [ 'member', 'album' ],
                        syntax : '<member> <album>',
                        example : `${bot.owner.username} Darkhorse`,
                        aliases : [ 'playsa', 'aplays' ]
                    },
                    {
                        name : 'lastfm playstrack',
                        description : 'Show your plays for a track.',
                        parameters : [ 'member', 'track' ],
                        syntax : '<member> <track>',
                        example : `${bot.owner.username} 4seasons`,
                        aliases : [ 'playst', 'tplays' ]
                    },
                    {
                        name : 'lastfm compare',
                        description : 'Compare your top artists with another member.',
                        parameters : [ 'member' ],
                        syntax : '(member)',
                        example : `${bot.owner.username}`,
                        aliases : [ 'taste', 'mutual', 'match' ]
                    }
                ],
                module : 'Last.fm Integration'
            }
        )
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !allCommands.includes(command)) {
            return bot.help(
                message, this
            )
        }

        const data = await bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
            bind : [
                message.author.id
            ]
        }).then(([results]) => results)

        if (!data.length && commands.username.includes(command)) {
            return bot.warn(
                message, error(
                    message.author, message.author, 'notConnected'  
                )
            )
        }

        switch (command) {
            case (command === 'set' ? command : command === 'link' ? command : command === 'connect' ? command : '') : {
                try {
                    const username = String(args[1])

                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[0]
                        )
                    }

                    const changeUsername = async () => {
                        if (String(args[1]).toLowerCase() === 'none') {
                            bot.db.query('DELETE FROM lastfm.usernames WHERE user_id = $1', {
                                bind : [
                                    message.author.id
                                ]
                            })
    
                            bot.approve(
                                message, `Your username has been **removed**.`
                            )
                        } else {
                            const results = await axios({
                                method : 'GET',
                                url : `http://ws.audioscrobbler.com/2.0/`,
                                params : {
                                    method : 'user.getinfo',
                                    user : username,
                                    api_key : process.env.LASTFM_API_KEY,
                                    format : 'json'
                                }
                            }).then((results) => results.data).catch(() => {})
        
                            if (!results) {
                                return bot.warn(
                                    message, `User [**${username}**](https://last.fm/user/${username}) was not found.`
                                )
                            }
        
                            const data = await bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                                bind : [
                                    message.author.id
                                ]
                            }).then(([results]) => results)
        
                            if (!data.length) {
                                bot.db.query('INSERT INTO lastfm.usernames (username, user_id) VALUES ($1, $2)', {
                                    bind : [
                                        results.user.name, message.author.id
                                    ]
                                })
                            } else {
                                if (data[0].username === results.user.name) {
                                    return bot.warn(
                                        message, `Your **Last.fm** username is already set as [**${results.user.name}**](https://last.fm/user/${results.user.name}).`
                                    )
                                }

                                await bot.db.query('UPDATE lastfm.usernames SET username = $1 WHERE user_id = $2', {
                                    bind : [
                                        results.user.name, message.author.id
                                    ]
                                })
                            }
    
                            const msg = await bot.neutral(
                                message, `Creating a new **Last.fm** library..`
                            )
    
                            const library = new Library(
                                bot, {
                                    username : results.user.name,
                                    message : message,
                                    msg : msg
                                }
                            )
    
                            await library.index()
        
                            bot.approve(
                                message, `Success, your **Last.fm** profile has been set as [**${results.user.name}**](https://last.fm/user/${results.user.name}).`, {
                                    edit : msg
                                }
                            )
                        }
                    }

                    const crowns = await bot.db.query('SELECT * FROM lastfm.crowns WHERE user_id = $1', {
                        bind : [
                            message.author.id
                        ]
                    }).then(([results]) => results)

                    if (crowns.length) {
                        await bot.confirm(
                            message, `Are you sure that you would like to change or remove your username?`, async () => {
                                await changeUsername()

                                await bot.db.query('DELETE FROM lastfm.crowns where user_id = $1', {
                                    bind : [
                                        message.author.id
                                    ]
                                })
                            }, { text : `Crowns that you have in other servers will be **removed** and **not restored**.` }
                        )
                    } else {
                        await changeUsername()
                    }
                } catch (error) {
                    return bot.error(
                        message, 'lastfm set', error
                    )
                }

                break
            }

            case (command === 'update' ? command : command === 'refresh' ? command : command === 'reload' ? command : command === 'index' ? command : '') : {
                try {
                    const msg = await bot.neutral(
                        message, `Updating your current **Last.fm** library..`
                    )

                    const library = new Library(
                        bot, {
                            username : data[0].username,
                            message : message,
                            msg : msg
                        }
                    )

                    await library.index()

                    bot.approve(
                        message, `Your **Last.fm** library has been updated.`, {
                            edit : msg
                        }
                    )
                } catch (error) {
                    return bot.error(
                        message, 'lastfm update', error
                    )
                }

                break
            }

            case (command === 'mode' ? command : command === 'embed' ? command : '') : {
                try {
                    const mode = String(args[1]).toLowerCase()

                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[2]
                        )
                    }

                    if (['none', 'check'].includes(mode)) {
                        switch (mode) {
                            case ('none') : {
                                break
                            }

                            case ('check') : {
                                break
                            }
                        }
                    } else {
                        const code = args.slice(1).join(' ')
                        
                        const data = await bot.db.query('SELECT * FROM lastfm.modes WHERE user_id = $1', {
                            bind : [
                                message.author.id
                            ]
                        }).then(([results]) => results)
    
                        if (!data.length) {
                            bot.db.query('INSERT INTO lastfm.modes (user_id, embed_code) VALUES ($1, $2)', {
                                bind : [
                                    message.author.id, code
                                ]
                            })
                        } else {
                            bot.db.query('UPDATE lastfm.modes SET embed_code = $1 WHERE user_id = $2', {
                                bind : [
                                    code, message.author.id
                                ]
                            })
                        }

                        bot.approve(
                            message, `Your **custom mode** has been set as\`\`\`${code}\`\`\``
                        )
                    }
                } catch (error) {
                    return bot.error(
                        message, 'lastfm mode', error
                    )
                }

                break
            }

            case (command === 'reactions' ? command : command === 'reaction' ? command : command === 'react' ? command : command === 'cr' ? command : '') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[3]
                        )
                    }

                    const upvote = await bot.converters.emoji(args[1])

                    if (!args[2]) {
                        return bot.warn(
                            message, `Missing a **downvote** reaction.`
                        )
                    }

                    const downvote = await bot.converters.emoji(args[2])

                    if (!upvote || !downvote) {
                        return bot.warn(
                            message, `Could not extract that **emote**. Maybe use one from this server instead?`
                        )
                    }

                    const data = await bot.db.query('SELECT * FROM lastfm.reactions WHERE user_id = $1', {
                        bind : [
                            message.author.id
                        ]
                    }).then(([results]) => results)

                    if (!data.length) {
                        bot.db.query('INSERT INTO lastfm.reactions (user_id, upvote, downvote) VALUES ($1, $2, $3)', {
                            bind : [
                                message.author.id, upvote.identifier, downvote.identifier
                            ]
                        })
                    } else {
                        bot.db.query('UPDATE lastfm.reactions SET upvote = $1 AND downvote = $2 WHERE user_id = $3', {
                            bind : [
                                upvote.identifier, downvote.identifier, message.author.id
                            ]
                        })
                    }

                    bot.approve(
                        message, `Set your **reactions** to ${upvote.emoji} and ${downvote.emoji}`
                    )
                } catch (error) {
                    return bot.error(
                        message, 'lastfm reactions', error
                    )
                }

                break
            }

            case (command === 'whoknows' ? command : command === 'wk' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsArtist = new WhoKnows( 
                    bot, data, 'artist'
                )

                await whoknowsArtist.execute(
                    message, args
                )

                break
            }

            case (command === 'wkalbum' ? command : command === 'whoknowsalbum' ? command : command === 'wka' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsAlbum = new WhoKnows(
                    bot, data, 'album'
                )

                await whoknowsAlbum.execute(
                    message, args
                )

                break
            }

            case (command === 'wktrack' ? command : command === 'whoknowstrack' ? command : command === 'wkt' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsTrack = new WhoKnows(
                    bot, data, 'track'
                )

                whoknowsTrack.execute(
                    message, args
                )

                break
            }

            case (command === 'globalwhoknows' ? command : command === 'globalwk' ? command : command === 'gwk' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsArtist = new WhoKnows(
                    bot, data, 'artist', true
                )

                whoknowsArtist.execute(
                    message, args
                )

                break
            }

            case (command === 'globalwkalbum' ? command : command === 'globalwka' ? command : command === 'gwka' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsAlbum = new WhoKnows(
                    bot, data, 'album', true
                )

                await whoknowsAlbum.execute(
                    message, args
                )

                break
            }

            case (command === 'globalwktrack' ? command : command === 'globalwkt' ? command : command === 'gwkt' ? command : '') : {
                message.channel.sendTyping()

                const whoknowsTrack = new WhoKnows(
                    bot, data, 'track', true
                )

                whoknowsTrack.execute(
                    message, args
                )

                break
            }

            case (command === 'topartists' ? command : command === 'topartist' ? command : command === 'artists' ? command : command === 'artist' ? command : command === 'tar' ? command : command === 'ta' ? command : '') : {
                message.channel.sendTyping()

                const topArtists = new Top(
                    bot, 'artist'
                )

                topArtists.execute(
                    message, args
                )

                break
            }

            case (command === 'topalbums' ? command : command === 'topalbum' ? command : command === 'albums' ? command : command === 'album' ? command : command === 'tab' ? command : command === 'tl' ? command : '') : {
                message.channel.sendTyping()

                const topAlbums = new Top(
                    bot, 'album'
                )

                topAlbums.execute(
                    message, args
                )

                break
            }

            case (command === 'toptracks' ? command : command === 'toptrack' ? command : command === 'tracks' ? command : command === 'track' ? command : command === 'ttr' ? command : command === 'tt' ? command : '') : {
                message.channel.sendTyping()

                const topTracks = new Top(
                    bot, 'track'
                )

                topTracks.execute(
                    message, args
                )

                break
            }

            case ('plays') : {
                message.channel.sendTyping()

                const playsArtist = new Plays( 
                    bot, data, 'artist'
                )

                await playsArtist.execute(
                    message, args
                )

                break
            }

            case (command === 'playsalbum' ? command : command === 'playsa' ? command : command === 'aplays' ? command : '') : {
                message.channel.sendTyping()

                const playsAlbum = new Plays( 
                    bot, data, 'album'
                )

                await playsAlbum.execute(
                    message, args
                )

                break
            }

            case (command === 'playstrack' ? command : command === 'playst' ? command : command === 'tplays' ? command : '') : {
                message.channel.sendTyping()

                const playsTrack = new Plays( 
                    bot, data, 'track'
                )

                await playsTrack.execute(
                    message, args
                )

                break
            }

            case ('recent') : {
                try {
                    const data = await bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                        bind : [ message.author.id ]
                    }).then(([results]) => results)

                    if (!data.length) {
                        return
                    }
                                        const results = await axios({
                                method : 'GET',
                                url : `http://ws.audioscrobbler.com/2.0/`,
                                params : {
                                    method : 'user.getrecenttracks',
                                    user : data[0].username,
                                    api_key : process.env.LASTFM_API_KEY,
                                    format : 'json'
                                }
                            }).then((results) => results.data).catch(() => {})

                            
                } catch (error) {
                    return bot.error(
                        message, 'recent', error
                    )
                }
            }

            case (command === 'compare' ? command : command === 'taste' ? command : command === 'mutual' ? command : command === 'match' ? command : '') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[16]
                        )
                    }

                    const data = await bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                        bind : [ message.author.id ]
                    }).then(([results]) => results)

                    if (!data.length) {
                        return
                    }

                    let artists = await bot.db.query('SELECT * FROM lastfm_library.artists WHERE user_id = $1', {
                        bind : [ message.author.id ]
                    }).then(([results]) => results)

                    const member = await bot.converters.member(message, args.slice(1).join(' '), { response : true })

                    if (!member) {
                        return
                    }

                    const memberData = await bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                        bind : [ member.user.id ]
                    }).then(([results]) => results)

                    if (!memberData.length) {
                        return bot.warn(
                            message, error(
                                member.user, message.author, 'notConnected'  
                            )
                        )
                    }

                    let memberArtists = await bot.db.query('SELECT * FROM lastfm_library.artists WHERE user_id = $1', {
                        bind : [ member.user.id ]
                    }).then(([results]) => results)

                    const commonArtists = artists.filter(artist => memberArtists.map(memberArtist => memberArtist.artist).includes(artist.artist)).length

                    const artists1 = artists.map((artist) => artist.artist)
                    const artists2 = memberArtists.map((artist) => artist.artist)

                    const percentage = (commonArtists / (artists1.length + artists2.length - commonArtists)) * 100

                    let comparisons = []

                    for (const artist of artists) {
                        const check = memberArtists.filter((element) => element.artist === artist.artist)[0]

                        let operator 

                        if (check) {
                            const plays = check.plays

                            switch (true) {
                                case (artist.plays > plays) : {
                                    operator = '>'
    
                                    break
                                }
    
                                case (artist.plays === plays) : {
                                    operator = '='
    
                                    break
                                }
    
                                case (artist.plays < plays) : {
                                    operator = '<'
    
                                    break
                                }
                            }
    
                            comparisons.push({
                                artist : `${artist.artist.slice(0, 16).trim()}${artist.artist.length > 16 ? '..' : ''}`,
                                plays : `${parseInt(artist.plays).toLocaleString()} ${operator} ${parseInt(plays).toLocaleString()}`,
                                raw : artist.plays 
                            })
                        }
                    }

                    comparisons = comparisons.sort((a, b) => b.raw - a.raw).slice(0, 10)

                    const longestName = Math.max(...comparisons.map(element => element.artist.length))
                    
                    const mappedArray = comparisons.map(element => ({
                        name : element.artist.padEnd(longestName, ' '),
                        value: element.plays
                    }))
                    
                    const mapped = mappedArray.map(element => `${element.name.padEnd(element.name.length + 1, ' ')}${element.value}`).join('\n')

                    message.channel.send({
                        embeds : [
                            new Discord.EmbedBuilder({
                                author : {
                                    name : String(message.member.displayName),
                                    iconURL : message.member.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                title : `Comparison - ${data[0].username} vs ${memberData[0].username}`,
                                description : `You both have **${commonArtists}** artists (${percentage.toFixed(0)}%) in common\n>>> \`\`\`${mapped}\`\`\``
                            }).setColor(bot.colors.neutral)
                        ]
                    })
                } catch (error) {
                    return bot.error(
                        message, 'lastfm compare', error
                    )
                }

                break
            }
        }
    }
}

class Library {
    constructor (bot, { username, message, msg }) {
        this.bot = bot
        this.username = username
        this.message = message
        this.msg = msg

        this.artists = [], this.albums = [], this.tracks = []

        this.totalArtists = null, this.totalAlbums = null, this.totalTracks = null

        this.artistsPerPage = 2000, this.albumsPerPage = 1000, this.tracksPerPage = 1000

        this.artistPage = 1, this.albumPage = 1, this.trackPage = 1
    }

    async query (type, page) {
        try {
            const converter = {
                'artist' : 'library.getArtists',
                'album' : 'user.getTopAlbums',
                'track' : 'user.getTopTracks'
            }

            const results = await fetch(`http://ws.audioscrobbler.com/2.0/?method=${converter[type]}&user=${this.username}&api_key=${process.env.LASTFM_API_KEY}&format=json&limit=${type === 'artist' ? '2000' : '1000'}&page=${page}`, {
                method : 'GET'
            }).then((results) => results.json())

            switch (type) {
                case ('artist') : {
                    this.artists = this.artists.concat(results.artists.artist)
                    this.totalArtists = parseInt(results.artists['@attr'].total)

                    break
                }

                case ('album') : {
                    this.albums = this.albums.concat(results.topalbums.album)
                    this.totalAlbums = parseInt(results.topalbums['@attr'].total)

                    break
                }

                case ('track') : {
                    this.tracks = this.tracks.concat(results.toptracks.track)
                    this.totalTracks = parseInt(results.toptracks['@attr'].total)

                    break
                }
            }
        } catch (error) {
            console.error('Library', error)
        }
    }

    async index () {
        try {
            this.bot.neutral(
                this.message, `Indexing your **Last.fm** artist library..`, {
                    edit : this.msg
                }
            )

            await this.query('artist', this.artistPage)

            while (this.artists.length < this.totalArtists) {
                this.artistPage++
                await this.query('artist', this.artistPage)
            }

            if (this.totalArtists === 0) {
                this.bot.warn(
                    this.message, `Aborted indexing your **Last.fm** artist library - No plays available!`, {
                        edit : this.msg
                    }
                )
            } else {
                this.bot.approve(
                    this.message, `Finished index of your **Last.fm** artist library.. (${this.totalArtists})`, {
                        edit : this.msg
                    }
                )
            }

            this.bot.neutral(
                this.message, `Indexing your **Last.fm** album library..`, {
                    edit : this.msg
                }
            )

            await this.query('album', this.albumPage)
            
            while (this.albums.length < this.totalAlbums) {
                this.albumPage++
                await this.query('album', this.albumPage)
            }

            if (this.totalAlbums === 0) {
                this.bot.warn(
                    this.message, `Aborted indexing your **Last.fm** album library - No plays available!`, {
                        edit : this.msg
                    }
                )
            } else {
                this.bot.approve(
                    this.message, `Finished index of your **Last.fm** album library.. (${this.totalAlbums})`, {
                        edit : this.msg
                    }
                )
            }

            this.bot.neutral(
                this.message, `Indexing your **Last.fm** track library..`, {
                    edit : this.msg
                }
            )

            await this.query('track', this.trackPage)
            
            while (this.tracks.length < this.totalTracks) {
                this.trackPage++
                await this.query('track', this.trackPage)
            }

            if (this.totalTracks === 0) {
                this.bot.warn(
                    this.message, `Aborted indexing your **Last.fm** track library - No plays available!`, {
                        edit : this.msg
                    }
                )
            } else {
                this.bot.approve(
                    this.message, `Finished index of your **Last.fm** track library.. (${this.totalTracks})`, {
                        edit : this.msg
                    }
                )
            }

            this.bot.neutral(
                this.message, `Saving your **Last.fm** artists, albums, and tracks..`, {
                    edit : this.msg
                }
            )

            await this.saveUserArtists()
            await this.saveUserAlbums()
            await this.saveUserTracks()

            return
        } catch (error) {
            console.error('Library', error)
        }
    }

    async saveUserArtists () {
        const { author } = this.message

        await this.bot.db.query('DELETE FROM lastfm_library.artists WHERE user_id = $1', {
            bind : [
                author.id
            ]
        })

        const libraryArtists = this.bot.db.define(
            'artists', {
                username : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false
                },
                user_id : {
                    type : sequelize.DataTypes.BIGINT,
                    allowNull : false,
                    primaryKey : true
                },
                artist : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false,
                    primaryKey : true
                },
                plays : {
                    type : sequelize.DataTypes.INTEGER,
                    allowNull : false
                }
            },
            {
                schema : 'lastfm_library',
                timestamps : false
            }
        )

        const userArtists = this.artists.map(({ name, playcount }) => ({
            username : this.username,
            user_id : author.id,
            artist : name,
            plays : playcount
        }))

        await libraryArtists.bulkCreate(
            userArtists, {
                ignoreDuplicates : true
            }
        )
    }

    async saveUserAlbums () {
        const { author } = this.message

        await this.bot.db.query('DELETE FROM lastfm_library.albums WHERE user_id = $1', {
            bind : [
                author.id
            ]
        })

        const libraryAlbums = this.bot.db.define(
            'albums', {
                username : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false
                },
                user_id : {
                    type : sequelize.DataTypes.BIGINT,
                    allowNull : false,
                    primaryKey : true
                },
                artist : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false,
                    primaryKey : true
                },
                album : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false,
                    primaryKey : true
                },
                plays : {
                    type : sequelize.DataTypes.INTEGER,
                    allowNull : false
                }
            },
            {
                schema : 'lastfm_library',
                timestamps : false
            }
        )

        const userAlbums = this.albums.map(({ artist, name, playcount }) => ({
            username : this.username,
            user_id : author.id,
            artist : artist.name,
            album : name,
            plays : playcount
        }))

        await libraryAlbums.bulkCreate(
            userAlbums, {
                ignoreDuplicates : true
            }
        )
    }

    async saveUserTracks () {
        const { author } = this.message

        await this.bot.db.query('DELETE FROM lastfm_library.tracks WHERE user_id = $1', {
            bind : [
                author.id
            ]
        })

        const libraryTracks = this.bot.db.define(
            'tracks', {
                username : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false
                },
                user_id : {
                    type : sequelize.DataTypes.BIGINT,
                    allowNull : false,
                    primaryKey : true
                },
                artist : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false,
                    primaryKey : true
                },
                track : {
                    type : sequelize.DataTypes.TEXT,
                    allowNull : false,
                    primaryKey : true
                },
                plays : {
                    type : sequelize.DataTypes.INTEGER,
                    allowNull : false
                }
            },
            {
                schema : 'lastfm_library',
                timestamps : false
            }
        )

        const userTracks = this.tracks.map(({ artist, name, playcount }) => ({
            username : this.username,
            user_id : author.id,
            artist : artist.name,
            track : name,
            plays : playcount
        }))

        await libraryTracks.bulkCreate(
            userTracks, {
                ignoreDuplicates : true
            }
        )
    }
}

class WhoKnows {
    constructor (bot, data, type, global = false) {
        this.bot = bot
        this.data = data
        this.type = type
        this.global = global
    }

    async execute (message, args) {
        let members = [], positions = [], name, artist

        if (!args[1]) {
            const recentTracks = await fetch(`http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=${this.data[0].username}&api_key=${process.env.LASTFM_API_KEY}&format=json`, {
                method : 'GET'
            }).then((results) => results.json()).catch(() => {})

            if (recentTracks.recenttracks.track.length === 0) {
                return
            }

            switch (this.type) {
                case ('artist') : {
                    name = recentTracks.recenttracks.track[0].artist['#text']
                    
                    break
                }

                case ('album') : {
                    name = recentTracks.recenttracks.track[0].album['#text'], artist = recentTracks.recenttracks.track[0].artist['#text']

                    break
                }

                case ('track') : {
                    name = recentTracks.recenttracks.track[0].name, artist = recentTracks.recenttracks.track[0].artist['#text']

                    break
                }
            }
        } else {
            if (['album', 'track'].includes(this.type)) {
                name = args.slice(1).join(' ')

                switch (this.type) {
                    case ('album') : {
                        const album = await axios({
                            method : 'GET',
                            url : `http://ws.audioscrobbler.com/2.0/?method=album.search&album=${name}&api_key=${process.env.LASTFM_API_KEY}&limit=1&format=json`
                        }).then((results) => results.data)

                        if (!album.results.albummatches.album.length) {
                            return
                        }

                        name = album.results.albummatches.album[0].name, artist = album.results.albummatches.album[0].artist

                        break
                    }

                    case ('track') : {
                        const track = await axios({
                            method : 'GET',
                            url : `http://ws.audioscrobbler.com/2.0/?method=track.search&track=${name}&api_key=${process.env.LASTFM_API_KEY}&limit=1&format=json`
                        }).then((results) => results.data)

                        if (!track.results.trackmatches.track.length) {
                            return
                        }

                        name = track.results.trackmatches.track[0].name, artist = track.results.trackmatches.track[0].artist

                        break
                    }
                }
            } else {
                name = args.slice(1).join(' ')
            }
        }

        const information = await fetch(`http://ws.audioscrobbler.com/2.0/?method=${this.type}.getinfo&${this.type}=${name}&api_key=${process.env.LASTFM_API_KEY}&autocorrect=1&format=json${['album', 'track'].includes(this.type) ? `&artist=${artist}` : ''}`, {
            method : 'GET'
        }).then((results) => results.json()).catch(() => {})

        if (!information) {
            return
        }

        console.log(information)
        
        name = information[this.type].name

        const cache = this.global ? null : await message.guild.members.fetch(), usernames = await this.bot.db.query('SELECT * FROM lastfm.usernames').then(([results]) => results)

        await Promise.all(
            usernames.map(async (I) => {
                const type = this.global ? 'user' : 'member', entity = type === 'user' ? await this.bot.users.fetch(this.bot.users.resolveId(I.user_id)).catch(() => {}) : await cache.get(I.user_id)

                if (entity) {
                    const [ usernameData, data ] = await Promise.all(
                        [
                            this.bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
                                bind : [
                                    type === 'user' ? entity.id : entity.user.id
                                ]
                            }).then(([results]) => results),
                            this.bot.db.query(`SELECT * FROM lastfm_library.${this.type}s WHERE user_id = $1 AND ${this.type} ILIKE $2`, {
                                bind : [
                                    type === 'user' ? entity.id : entity.user.id, name
                                ]
                            }).then(([results]) => results)
                        ]
                    )

                    if (!usernameData.length || !data.length) return

                    const object = {
                        id : type === 'user' ? entity.id : entity.user.id,
                        text : `[**${type === 'user' ? entity.tag : entity.user.tag}**](https://last.fm/user/${usernameData[0].username})`,
                        plays : parseInt(data[0].plays)
                    }

                    positions.push(object)

                    if (data[0].plays > 0) {
                        return members.push(object)
                    }
                }
            })
        )

        const [ sortedP, sortedM ] = await Promise.all(
            [
                Promise.resolve(
                    positions.sort((a, b) => parseInt(b.plays) - parseInt(a.plays))
                ),
                Promise.resolve(
                    members.sort((a, b) => parseInt(b.plays) - parseInt(a.plays))
                )
            ]
        )

        const mappedM = sortedM.map((I) => { return I })

        if (!mappedM.length) {
            return this.bot.warn(
                message, `No results were found for **${name}**`
            )
        }

        const position = sortedP.find((member) => member.id === message.author.id) || { plays : 0 }
        const rank = sortedM.find((member) => member.id === message.author.id) ? `#${sortedP.indexOf(position) + 1}` : 'Unranked'

        const embeds = [], entries = mappedM.list(10)

        let index = 0, crown = null, crownPlays = 0

        for (const entry of entries) {
            const mapped = entry.map((I) => {
                let display

                ++index
                display = `\`${index}\``

                if (index === 1 && this.type === 'artist' && !this.global) {
                    display = ':crown:'
                    crown = I.id, crownPlays = I.plays
                }

                return `${display} ${I.text} has **${I.plays.toLocaleString()}** ${I.plays === 1 ? 'play' : 'plays'}`
            }).join('\n')

            embeds.push(
                new Discord.EmbedBuilder({
                    author : {
                        name : String(message.member.displayName),
                        iconURL : message.member.displayAvatarURL({
                            dynamic : true
                        })
                    },
                    title : `Top${this.global ? ' Global ' : ' '}Listeners for ${this.type} ${name}`,
                    description : `${mapped}\nYour plays: **${position.plays.toLocaleString()}** - Rank: \`${rank}\``
                }).setColor(this.bot.colors.neutral)
            )
        }

        await new this.bot.paginator(
            message, {
                embeds : embeds,
                entries : index,
                text : `Page {page} of {pages} ({entries} entries)\n${position.plays === 0 ? `Missing plays? Use "lastfm update" to index them` : ''}`
            }
        ).construct()

        if (crown) {
            const crownMember = await cache.get(crown)

            if (crownMember) {
                const cData = await this.bot.db.query('SELECT * FROM lastfm.crowns WHERE guild_id = $1 AND artist ILIKE $2', {
                    bind : [
                        message.guild.id, name
                    ]
                }).then(([results]) => results)

                if (cData.length) {
                    if (cData[0].user_id === crownMember.user.id) return

                    const oldCrownMember = await this.bot.users.fetch(this.bot.users.resolveId(cData[0].user_id)).catch(() => {})

                    await this.bot.db.query('UPDATE lastfm.crowns SET user_id = $1, plays = $2 WHERE guild_id = $3 AND artist ILIKE $4', {
                        bind : [
                            crownMember.user.id, crownPlays, message.guild.id, name
                        ]
                    })

                    await this.bot.neutral(
                        message, `\`${crownMember.user.tag}\` stole the crown from \`${oldCrownMember.tag}\` for **${name}**!`, {
                            removeMention : true,
                            reply : false
                        }
                    )
                } else {
                    await this.bot.db.query('INSERT INTO lastfm.crowns (guild_id, user_id, artist, plays) VALUES ($1, $2, $3, $4)', {
                        bind : [
                            message.guild.id, crownMember.user.id, name, crownPlays
                        ]
                    })

                    await this.bot.neutral(
                        message, `\`${crownMember.user.tag}\` claimed the crown for **${name}**!`, {
                            removeMention : true,
                            reply : false
                        }
                    )
                }
            }
        }
    }
}

class TopTen {
    constructor (bot, type) {
        this.bot = bot
        this.type = type
    }

    async execute (message, args) {
        let member, isArgs

        if (args[1]) {
            member = await this.bot.converters.member(
                message, args[1]
            ), isArgs = true

            if (!member) {
                member = message.member, isArgs = false
            }
        } else {
            member = message.member, isArgs = false
        }

        const data = await this.bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
            bind : [
                member.id
            ]
        }).then(([results]) => results)

        if (!data.length) {
            return this.bot.warn(
                message, error(
                    member.user, message.author, 'notConnected'  
                )
            )
        }
    }
}

class Plays {
    constructor (bot, data, type) {
        this.bot = bot
        this.data = data
        this.type = type
    }

    async execute (message, args) {
        let member, isArgs

        if (args[1]) {
            member = await this.bot.converters.member(
                message, args[1]
            ), isArgs = true

            if (!member) {
                member = message.member, isArgs = false
            }
        } else {
            member = message.member, isArgs = false
        }

        const data = await this.bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
            bind : [
                member.id
            ]
        }).then(([results]) => results)

        if (!data.length) {
            return this.bot.warn(
                message, error(
                    member.user, message.author, 'notConnected'  
                )
            )
        }

        let name = isArgs ? args.slice(2).join(' ') : args.slice(1).join(' '), artist

        if (!name) {
            const recentTracks = await axios({
                method : 'GET',
                url : 'http://ws.audioscrobbler.com/2.0/',
                params : {
                    method : 'user.getrecenttracks',
                    user : data[0].username,
                    api_key : process.env.LASTFM_API_KEY,
                    format : 'json'
                }
            }).then((results) => results.data).catch(() => {})

            if (recentTracks.recenttracks.track.length === 0) {
                return
            }

            switch (this.type) {
                case ('artist') : {
                    name = recentTracks.recenttracks.track[0].artist['#text']
                    
                    break
                }

                case ('album') : {
                    name = recentTracks.recenttracks.track[0].album['#text'], artist = recentTracks.recenttracks.track[0].artist['#text']

                    break
                }

                case ('track') : {
                    name = recentTracks.recenttracks.track[0].name, artist = recentTracks.recenttracks.track[0].artist['#text']

                    break
                }
            }
        } else {
            if (['album', 'track'].includes(this.type)) {
                switch (this.type) {
                    case ('album') : {
                        const album = await axios({
                            method : 'GET',
                            url : `http://ws.audioscrobbler.com/2.0/?method=album.search&album=${name}&api_key=${process.env.LASTFM_API_KEY}&limit=1&format=json`
                        }).then((results) => results.data)

                        if (!album.results.albummatches.album.length) {
                            return
                        }

                        name = album.results.albummatches.album[0].name, artist = album.results.albummatches.album[0].artist

                        break
                    }

                    case ('track') : {
                        const track = await axios({
                            method : 'GET',
                            url : `http://ws.audioscrobbler.com/2.0/?method=track.search&track=${name}&api_key=${process.env.LASTFM_API_KEY}&limit=1&format=json`
                        }).then((results) => results.data)

                        if (!track.results.trackmatches.track.length) {
                            return
                        }

                        name = track.results.trackmatches.track[0].name, artist = track.results.trackmatches.track[0].artist

                        break
                    }
                }
            }
        }

        const information = await axios({
            method : 'GET',
            url : `http://ws.audioscrobbler.com/2.0/?method=${this.type}.getinfo&${this.type}=${name}&api_key=${process.env.LASTFM_API_KEY}&username=${data[0].username}&autocorrect=1&format=json${['album', 'track'].includes(this.type) ? `&artist=${artist}` : ''}`
        }).then((results) => results.data).catch(() => {})

        if (!information) {
            return
        }

        const user = await this.bot.users.fetch(this.bot.users.resolveId(data[0].user_id)).catch(() => {})
        const operator = data[0].user_id === this.data[0].user_id ? `You have` : `**${user.tag}** has`

        let plays, url

        const item = information[this.type]

        console.log(item)

    console.log(this.type)

        if (['album', 'track'].includes(this.type)) {
            console.log(item.userplaycount)
            console.log('Album, Track')
            plays = item.userplaycount
        } else {
            console.log(item.stats.userplaycount)
            console.log('Artist')
            plays = item.stats.userplaycount
        }

        name = item.name, url = item.url

        const artistOperator = artist ? ` by **${artist}**` : ''

        this.bot.neutral(
            message, `${operator} **${parseInt(plays).toLocaleString()}** plays for [**${name}**](${url})${artistOperator}`
        )
    }
}

class Top {
    constructor (bot, type) {
        this.bot = bot
        this.type = type
    }

    async execute (message, args) {
        let member, isArgs

        if (args[1]) {
            member = await this.bot.converters.member(
                message, args[1]
            ), isArgs = true

            if (!member) {
                member = message.member, isArgs = false
            }
        } else {
            member = message.member, isArgs = false
        }

        const data = await this.bot.db.query('SELECT * FROM lastfm.usernames WHERE user_id = $1', {
            bind : [
                member.id
            ]
        }).then(([results]) => results)

        if (!data.length) {
            return bot.warn(
                message, error(
                    member.user, message.author, 'notConnected'  
                )
            )
        }

        const period = this.period(isArgs ? args[2] : args[1])

        const top = await axios({
            method : 'GET',
            url : `http://ws.audioscrobbler.com/2.0/?method=user.gettop${this.type}s&user=${data[0].username}&api_key=${process.env.LASTFM_API_KEY}&limit=10${period.period}&format=json`,
        }).then((results) => results.data)

        console.log(top)

        const items = top[`top${this.type}s`][`${this.type}`]

        const embeds = [], entries = items.list(10)

        let index = 0

        for (const entry of entries) {
            const mapped = entry.map((I) => {
                ++index

                const plays = parseInt(I.playcount).toLocaleString()

                return `\`${index}\` [**${I.name}**](${I.url}) ${this.type === 'track' || this.type === 'album' ? `by **${I.artist.name}**` : ''} (${plays} ${plays === 1 ? 'play' : 'plays'})`
            }).join('\n')

            const converter = {
                'artist' : 'Top Artists',
                'album' : 'Top Albums',
                'track' : 'Top Tracks'
            }

            embeds.push(
                new Discord.EmbedBuilder({
                    author : {
                        name : String(message.member.displayName),
                        iconURL : message.member.displayAvatarURL({
                            dynamic : true
                        })
                    },
                    title : `${converter[this.type]} (${period.type}) - ${data[0].username}`,
                    description : mapped
                }).setColor(this.bot.colors.neutral)
            )
        }

        message.channel.send({
            embeds : [
                embeds[0]
            ]
        })
    }

    period (str =  '') {
        const periodMap = {
            '1w' : {
                type : 'Past Week',
                period : '&period=7day'
            },
            '1week' : {
                type : 'Past Week',
                period : '&period=7day'
            },
            '7d' : {
                type : 'Past Week',
                period : '&period=7day'
            },
            '7days' : {
                type : 'Past Week',
                period : '&period=7day'
            },
            '1m' : {
                type : 'Past Month',
                period : '&period=1month'
            },
            '1month' : {
                type : 'Past Month',
                period : '&period=1month'
            },
            '30d' : {
                type : 'Past Month',
                period : '&period=1month'
            },
            '30days' : {
                type : 'Past Month',
                period : '&period=1month'
            },
            '3m' : {
                type : 'Past 3 Months',
                period : '&period=3months'
            },
            '3months' : {
                type : 'Past 3 Months',
                period : '&period=3months'
            },
            '6m' : {
                type : 'Past 6 Months',
                period : '&period=6months'
            },
            '6months' : {
                type : 'Past 6 Months',
                period : '&period=6months'
            },
            '1y' : {
                type : 'Past Year',
                period : '&period=12month'
            },
            '1year' : {
                type : 'Past Year',
                period : '&period=12month'
            },
            '12m' : {
                type : 'Past Year',
                period : '&period=12month'
            },
            '12month' : {
                type : 'Past Year',
                period : '&period=12month'
            }
        }

        return periodMap[str.toLowerCase()] || {
            type : 'Overall',
            period : ''
        }
    }
}