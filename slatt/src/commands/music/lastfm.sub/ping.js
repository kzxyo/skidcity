const Subcommand = require('../../Subcommand.js');
const ms = require('parse-ms')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'ping',
            aliases: ['latency'],
            type: client.types.LASTFM,
            usage: 'lastfm albumplays [album]',
            description: 'View your playcount for a album',
        });
    }
    async run(message, args) {
        const fetch = require('node-fetch')
        const now = Date.now()
        fetch('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=drake&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1')
        .then(response => response.json())
        .then(res => {
            this.send_info(message, `it took ${ms(Date.now() - now).milliseconds}ms to ping **Last.fm**`)
        })
    }
}