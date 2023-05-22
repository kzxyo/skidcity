const Command = require('../Command.js');
var fetch = require('node-fetch');

module.exports = class Soundcloud extends Command {
    constructor(client) {
        super(client, {
            name: 'soundcloud',
            subcommands: ['soundcloud'],
            description: `Search soundcloud for a track`,
            usage: `soundcloud [track]`,
            aliases: ["sc"],
            type: client.types.LASTFM,
        });
    }

    async run(message, args) {
        let name
        const {
            LastfmUsers,
        } = require('../../utils/db.js');
        const user = await LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        if (user === null && !args[0]) {
            return this.link_lastfm(message, message.author)
        }
        if (user && !args[0]) {
            let recent = await this.lastfm.user_getrecent(user.username)
            if (!recent.recenttracks) return this.send_error(message, 1, `You do not have any **recent tracks** to be displayed`)
            let artist = recent.recenttracks.track[0].artist['#text']
            name = recent.recenttracks.track[0].name + ' ' + artist
        } else if (!user || user && args[0]) {
            name = args.join(' ')
        }
        fetch(`https://api-v2.soundcloud.com/search/tracks?q=${name}&sc_a_id=f09194f537af8a047e346012b1027e9b2462a387&variant_ids=2062&facet=genre&user_id=351211-547049-609646-716004&client_id=6JcMSl6wQUuPYeBzmXIOpxpp2VlPrIXE&limit=1&offset=0&linked_partitioning=1&app_version=1622710435&app_locale=en`, {
                headers: {
                    'Connection': 'keep-alive',
                    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Authorization': 'OAuth 2-292593-994587358-Af8VbLnc6zIplJ',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
                    'Origin': 'https://soundcloud.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://soundcloud.com/',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            }).then(response => response.json())
            .then(res => {
                message.channel.send(res.collection[0].permalink_url)
            })
    }
}