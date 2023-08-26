const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

module.exports = class Play extends Command {
    constructor (bot) {
        super (bot, 'play', {
            description : 'Enqueue a song for playback',
            parameters : [ 'query' ],
            syntax : '<query>',
            example : 'Dro Kenji - Vanish',
            aliases : [ 'p', 'queue', 'q' ],
            module : 'Music'
        })
    }

    async execute (bot, message, args) {
        try {
            if (!message.member.voice.channel) {
                return message.warn(`You aren't connected to a **voice channel**`)
            }

            if (args[0] || message.attachments.first()) {
                const player = bot.Lavalink.create({
                    guild : message.guild.id,
                    voiceChannel : message.member.voice.channel.id,
                    textChannel : message.channel.id,
                    selfDeafen : true,
                    volume : 100
                })

                if (player.state !== 'CONNECTED') {
                    player.connect()
                } else if (message.member.voice.channel.id !== message.guild.members.me.voice.channel.id) {
                    return message.warn(`You're in a different **voice channel** than me`)
                }

                let query

                if (args[0]) {
                    const url = /^(https?:\/\/)?(www\.)?[^\s/$.?#]+\.[^\s]*$/, allowed = [
                        /^https?:\/\/(www\.)?youtube\.com\//,
                        /^https?:\/\/(www\.)?music\.youtube\.com\//,
                        /^https?:\/\/(www\.)?soundcloud\.com\//,
                        /^https?:\/\/(www\.)?open\.spotify\.com\//
                    ]
                    
                    if (url.test(args[0]) && !allowed.some((regex) => regex.test(args[0]))) {
                        args[0] = `https://proxy.blair.win/?url=${args[0]}`
                    }
                } else {
                    args[0] = message.attachments.first().url
                }

                try {
                    query = await player.search(args.join(' '), message.author)

                    if (query.loadType === 'LOAD_FAILED') {
                        if (!player.queue.current) player.destroy()
                        
                        throw query.exception
                    }
                } catch (error) {
                    return message.warn(`Failed to fetch that **track**`)
                }

                switch (query.loadType) {
                    case ('NO_MATCHES') : {
                        if (!player.queue.current) player.destroy()

                        return message.warn(`Couldn't find a track for **${args.join(' ')}**`)
                    }

                    case ('PLAYLIST_LOADED') : {
                        player.queue.add(query.tracks)

                        let text = null

                        if (!player.playing && !player.paused) {
                            player.play()

                            text = `Now playing [**${query.tracks[0].title}**](${query.tracks[0].uri})`
                        }

                        return message.neutral(`Enqueued **${query.tracks.length.toLocaleString()} tracks** from [**${query.playlist.name}**](${query.playlist.uri || args[0].split('?si=')[0]})`, {
                            text : text
                        })
                    }

                    default : {
                        player.queue.add(query.tracks[0])

                        if (!player.playing && !player.paused && !player.queue.size) {
                            player.play()

                            message.neutral(`Now playing [**${query.tracks[0].title}**](${query.tracks[0].uri})`)
                        } else {
                            message.neutral(`Enqueued  [**${query.tracks[0].title}**](${query.tracks[0].uri})`)
                        }

                        return message.react('✅')
                    }
                }
            } else {
                const player = bot.Lavalink.get(message.guild.id)

                if (!player || !player.queue.current) {
                    return message.warn(`There isn't a **player** currently active`)
                }

                const queue = player.queue

                const position = player.position
                const duration = queue.current.duration
                
                const positionInSeconds = Math.floor(position / 1000)
                const durationInSeconds = Math.floor(duration / 1000)
                
                const hoursPosition = Math.floor(positionInSeconds / 3600)
                const minutesPosition = Math.floor((positionInSeconds % 3600) / 60)
                const secondsPosition = positionInSeconds % 60
                
                const hoursDuration = Math.floor(durationInSeconds / 3600)
                const minutesDuration = Math.floor((durationInSeconds % 3600) / 60)
                const secondsDuration = durationInSeconds % 60
                
                const remainingSeconds = durationInSeconds - positionInSeconds
                const timestamp = `${hoursPosition > 0 ? hoursPosition.toString().padStart(2, '0') + ':' : ''}${minutesPosition.toString().padStart(2, '0')}:${secondsPosition.toString().padStart(2, '0')}/${hoursDuration > 0 ? hoursDuration.toString().padStart(2, '0') + ':' : ''}${minutesDuration.toString().padStart(2, '0')}:${secondsDuration.toString().padStart(2, '0')}`

                const embed = new Discord.EmbedBuilder({
                    author : {
                        name : message.member.displayName,
                        iconURL : message.member.displayAvatarURL()
                    },
                    title : `Queue in ${message.member.voice.channel.name}`,
                    description : `Listening to [**${queue.current.title.slice(0, 21)}${queue.current.title.length > 21 ? '..' : ''}**](${queue.current.uri}) - ${queue.current.requester}\n> **${remainingSeconds} seconds** left of this song \`${timestamp}\``
                }).setColor(bot.colors.neutral)

                let embeds = [], index = 0

                if (queue.size > 0) {
                    const pages = queue.map((track) => track).list(10)

                    embeds = await Promise.all(
                        pages.map((page) => {
                            const entries = page.map((I) => {
                                return `\`${++index}\` [**${I.title.slice(0, 21)}${I.title.length > 21 ? '..' : ''}**](${I.uri}) - ${I.requester}`
                            }).join('\n')

                            const description = `${embed.data.description}\n\n${entries}`

                            return new Discord.EmbedBuilder(embed).setDescription(description)
                        })
                    )
                } else {
                    embeds = [
                        embed
                    ]
                }

                await new bot.paginator(
                    message, {
                        embeds : embeds
                    }
                ).construct()
            }
        } catch (error) {
            return message.error(error)
        }
    }
}