const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'match',
            type: client.types.LASTFM,
            usage: 'lastfm match [member]',
            description: 'Check your artist percentage match with another member',
        });
    }
    async run(message, args) {
        if (!args[0]) return this.help(message)
        const member = this.functions.get_member(message, args.join(' '))
        if (!member) {
            return this.invalidUser(message)
        } else {
            const {
                LastfmUsers,
            } = require('../../../utils/db.js')
            const check = await LastfmUsers.findOne({
                where: {
                    userID: message.author.id
                }
            })
            if (!check) {
                return this.link_lastfm(message, message.author)
            }
            const user = await LastfmUsers.findOne({
                where: {
                    userID: member.id
                }
            })
            if (!user) {
                return this.link_lastfm(message, member)
            }
            const author_artists = this.db.get(`Library_${message.author.id}`)
            const opp_artists = this.db.get(`Library_${member.id}`)
            if (!author_artists) return this.send_error(message, 1, `Your library does not have any artists to be displayed`)
            if (!opp_artists) return this.send_error(message, 1, `**${member.user.tag}**'s library does not have any artists to be displayed`)
            const artists = await author_artists.lib
            const arr = []
            const failed = []
            for (const artist of artists) {
                const is = opp_artists.lib.find(a => a.name === artist.name)
                if (is) {
                    arr.push({
                        artist: artist.name,
                        plays: is.playcount,
                        author_plays: this.db.get(`Library_${message.author.id}`).lib.find(a => a.name === artist.name).playcount
                    })
                } else {
                    failed.push({
                        fill: 'fill'
                    })
                }
            }
            if (!arr.length) {
                return this.send_info(message, `You and **${member.user.username}** do not have any artists in common`)
            }
            return this.send_info(message, `You and **${member.user.username}** have a artist match of **${Math.round((arr.length / author_artists.lib.length) * 100)}%**`)
        }
    }
}