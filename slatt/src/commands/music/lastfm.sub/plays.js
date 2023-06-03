const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'plays',
            type: client.types.LASTFM,
            usage: 'lastfm albumplays [artist]',
            description: 'View your playcount for a artist',
        });
    }
    async run(message, args) {

        message.channel.sendTyping()
   
        const {
            LastfmUsers,
        } = require('../../../utils/db.js');
        let member = message.mentions.members.first() || message.member
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let rec = await this.lastfm.user_getrecent(user.username)
        let recent = rec.recenttracks.track[0].artist['#text']
        let artist
        if (message.mentions.members.first()) artist = args.slice(1).join(' ') || recent
        if (!message.mentions.members.first()) artist = args.join(' ') || recent
        let artist_info = await this.lastfm.artist_getinfo(user.username, artist)
        if (!artist_info.artist) {
            return this.send_error(message, 1, `There was no artist named **${artist}** in **${user.username}**'s library`)
        }
        let scrobbles = artist_info.artist.stats.userplaycount
        let who
        if (!message.mentions.members.first()) who = `You have`
        if (message.mentions.members.first()) who = `**${member.user.tag}** has`
        return this.send_info(message, `${who} **${scrobbles}** plays for [${artist}](https://last.fm/music/${encodeURIComponent(artist)})`)
    }
}