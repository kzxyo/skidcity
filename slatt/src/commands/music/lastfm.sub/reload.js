const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')

module.exports = class Embed extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'reload',
            aliases: ['update', 'rl'],
            type: client.types.LASTFM,
            usage: 'lastfm reload',
            description: 'Update your playcounts for artists, tracks and albums',
        });
    }
    async run(message, args) {
        const {
            LastfmUsers,
        } = require('../../../utils/db.js');
        const user = await LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, message.author)
        }
        const reloading = new MessageEmbed().setDescription(`<:info:828536926603837441> ${message.author} Reloading your library, please wait..`).setColor("#78c6fe")
        const msg = await message.channel.send({embeds: [reloading]})
        let artist_info = await this.lastfm.user_getlibrary(user.username)
        const artists = artist_info.artists.artist
        let track_info = await this.lastfm.get_toptracks(user.username)
        const tracks = track_info.toptracks.track
        let album_info = await this.lastfm.get_topalbums(user.username)
        const albums = album_info.topalbums.album
        if (artists.length) {
            let a_a = []
            for(const a of artists) {
                a_a.push({
                    name: a.name,
                    playcount: a.playcount
                })
            }
            this.db.set(`Library_${message.author.id}`, {
                user: user.username,
                lib: a_a
            })
        }
        if (tracks.length) {
            let t_a = []
            for(const a of tracks) {
                t_a.push({
                    name: a.name,
                    playcount: a.playcount
                })
            }
            this.db.set(`Tracks_${message.author.id}`, {
                user: user.username,
                lib: t_a
            })
        }
        if (albums.length) {
            let al_a = []
            for(const a of albums) {
                al_a.push({
                    name: a.name,
                    playcount: a.playcount
                })
            }
            this.db.set(`Albums_${message.author.id}`, {
                user: user.username,
                lib: al_a
            })
        }
        const em = new MessageEmbed().setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Your last.fm library was reloaded: **${artists.length}** artists, **${albums.length}** albums, **${tracks.length}** tracks updated`).setColor("#007f00")
        msg.edit({embeds: [em]})
    }
}