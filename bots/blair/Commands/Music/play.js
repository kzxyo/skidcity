const Command = require('../../Structures/Base/Command.js')

const { QueryType } = require('discord-player')
const { EmbedBuilder } = require('discord.js')

module.exports = class Play extends Command {
    constructor (Client) {
        super (Client, 'play', {
            Aliases : [ 'queue', 'q', 'p' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (Message.author.id !== '944099356678717500') return Message.channel.send('command not available yet...')
        const Player = require('../../Structures/Player.js')

        try {
            if (Arguments[0]) {
                const TrackTitle = Arguments.join(' ')

                if (!Message.member.voice.channel) return;

                if (false) {
                    return new Client.Embed(
                        Message, `You are not connected to the same **Voice Channel** as me.`
                    )
                }

                const SearchResult = await Player.search(TrackTitle, {
                    requestedBy : Message.author,
                    searchEngine : QueryType.AUTO
                })

                const Queue = await Player.createQueue(Message.guild, {
                    metadata : {
                        channel : Message.channel,
                        voice : Message.member.voice.channel,
                        guild : Message.guild
                    }
                })

                Queue.options = Player.options
                
                if (!Queue.connection) await Queue.connect(Message.member.voice.channel)

                console.log(Queue.playing)

                if (Queue.current) {
                    new Client.Embed(
                        Message, `Added [${SearchResult.tracks[0].title}](${SearchResult.tracks[0].url}) to the **Queue** - ${Message.author}`
                    )
                }

                SearchResult.playlist ? Queue.addTracks(SearchResult.tracks) : Queue.addTrack(SearchResult.tracks[0])

                if (!Queue.playing) await Queue.play()
            } else {
                const Queue = Player.getQueue(Message.guild)    

                if (!Queue?.playing) {
                    return new Client.Embed(
                        Message, `Nothing in the **Queue** to play.`
                    )
                }

                const CurrentTrack = Queue.current

                const Results = await Player.search(CurrentTrack.url, { 
                    requestedBy : Message.author, 
                    searchEngine : QueryType.AUTO 
                })

                const Tracks = Queue.tracks.slice(0, 5).map((Map, Index) => { 
                    return `\`${Index + 1}\` [**${Map.title}**](${Map.url}) [${Map.requestedBy}]`
                })

                Message.channel.send({
                    embeds : [
                        new EmbedBuilder({
                            author : {
                                name : Message.member.displayName,
                                iconURL : Message.member.displayAvatarURL({
                                    dynamic : true
                                })
                            },
                            title : `Queue in ${Message.member.voice.channel.name}`,
                            description : `Now Playing [${CurrentTrack.title}](${CurrentTrack.url}) by **${Results.tracks[0].author}** [${CurrentTrack.requestedBy}]\n**0 seconds** left of this track \`${Results.tracks[0].duration}\`/\`${Results.tracks[0].duration}\``
                        }).setColor(Client.Color)
                    ]
                })
            }
        } catch (Error) {
            return new Client.Error(
                Message, 'play', Error
            )
        }
    }
}