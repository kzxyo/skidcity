const Command = require('../../Structures/Base/command.js')

const API = require('spotify-web-api-node'), SpotifyClient = new API({ clientId : process.env.SPOTIFY_CLIENT_ID, clientSecret : process.env.SPOTIFY_CLIENT_SECRET })

module.exports = class Spotify extends Command {
    constructor (bot) {
        super (bot, 'spotify', {
            description : 'Search for a song on Spotify',
            parameters : [ 'query' ],
            syntax : '(query)',
            example : 'PayDay by Yuno Miles',
            aliases : [ 'sptrack', 'sp' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
            const query = args.join(' ')

            if (!args[0]) {
                return bot.help(
                    message, this
                )
            }

            message.channel.sendTyping()

            const credentials = await SpotifyClient.clientCredentialsGrant()
            SpotifyClient.setAccessToken(credentials.body['access_token'])

            const tracks = await SpotifyClient.searchTracks(query), track = tracks.body.tracks.items[0]

            if (!track) {
                return bot.warn(
                    message, `Couldn't find any results for **${query}**`
                )
            }

            message.reply(track.external_urls.spotify)
        } catch (error) {
            return bot.error(
                message, 'spotify', error
            )
        }
    }
}