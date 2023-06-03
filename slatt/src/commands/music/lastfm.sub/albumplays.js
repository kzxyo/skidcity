const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'albumplays',
            aliases: ['aplays', 'playsa'],
            type: client.types.LASTFM,
            usage: 'lastfm albumplays [album]',
            description: 'View your playcount for a album',
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
        let recent = rec.recenttracks.track[0].album['#text'] + ' ' + rec.recenttracks.track[0].artist['#text']
        let album
        if (member !== message.member) album = args.slice(1).join(' ') || recent
        if (member === message.member) album = args.slice(0).join(' ') || recent
        let data = await this.lastfm.album_search(album)
        let album_info = await this.lastfm.album_getinfo(user.username, data.results.albummatches.album[0].artist, data.results.albummatches.album[0].name)
        if (!album_info.album) {
            return this.send_error(message, 1, `There was no track named **${album}** in **${user.username}**'s library`)
        }
        let scrobbles = album_info.album.userplaycount
        let who
        if (member === message.member) who = `You have`
        if (member !== message.member) who = `**${member.user.tag}** has`
        return this.send_info(message, `${who} **${scrobbles}** plays for album [${data.results.albummatches.album[0].name}](https://last.fm/music/${encodeURIComponent(data.results.albummatches.album[0].name.replace(' ', '+'))}) by **${data.results.albummatches.album[0].artist}**`)
    }
}