const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'trackplays',
            aliases: ['tplays', 'playst'],
            type: client.types.LASTFM,
            usage: 'lastfm trackplays [track]',
            description: 'View your playcount for a track',
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
        let recent = rec.recenttracks.track[0].name + ' ' + rec.recenttracks.track[0].artist['#text']
        let track
        if (member !== message.member) track = args.slice(2).join(' ') || recent
        if (member === message.member) track = args.slice(1).join(' ') || recent
        let data = await this.lastfm.track_search(track)
        let track_info = await this.lastfm.track_getinfo(user.username, data.results.trackmatches.track[0].artist, data.results.trackmatches.track[0].name)
        if (!track_info.track) {
            return this.send_error(message, 1, `There was no track named **${rec.recenttracks.track[0].name}** in **${user.username}**'s library`)
        }
        let scrobbles = track_info.track.userplaycount
        let who
        if (member === message.member) who = `You have`
        if (member !== message.member) who = `**${member.user.tag}** has`
        return this.send_info(message, `${who} **${scrobbles}** plays for track [${data.results.trackmatches.track[0].name}](https://last.fm/music/${encodeURIComponent(data.results.trackmatches.track[0].name.replace(' ', '+'))}) by **${data.results.trackmatches.track[0].artist}**`)    }
}