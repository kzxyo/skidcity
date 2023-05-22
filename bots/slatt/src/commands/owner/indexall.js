const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');
module.exports = class BlastCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'indexall',
            aliases: ['index', 'indexserver'],
            subcommands: ['index'],
            usage: 'index',
            type: client.types.OWNER,
            description: "Updates everyones playcount in your server to increase 'lastfm whoknows' speeds",
        });
    }
    async run(message, args) {
        const {
            LastfmUsers,
        } = require('../../utils/db.js');
        let arr = []
        const users = await LastfmUsers.findAll()
        const msg = await message.channel.send(new MessageEmbed().setDescription(`<:info:828536926603837441> ${message.author} **${users.length}** indexing`).setColor("#78c6fe"))
        for (const id of users) {
            let artist_info = await this.lastfm.user_getlibrary(id.username)
            const artists = artist_info.artists
            let track_info = await this.lastfm.get_toptracks(id.username)
            const tracks = track_info.toptracks
            let album_info = await this.lastfm.get_topalbums(id.username)
            const albums = album_info.topalbums
            if (artist_info.artists && track_info.toptracks && album_info.topalbums) {
                let library = artist_info.artists.artist
                let check = this.db.get(`Library_${id.userID}`)
                if (!check && artists.artist.length && tracks.track.length && albums.album.length) {
                    this.db.set(`Library_${id.userID}`, {
                        user: id.username,
                        lib: artists.artist
                    })
                    this.db.set(`Tracks_${id.userID}`, {
                        user: id.username,
                        lib: tracks.track
                    })
                    this.db.set(`Albums_${id.userID}`, {
                        user: id.username,
                        lib: albums.album
                    })
                    message.client.logger.info(id.username+' indexed')
                }
                arr.push({
                    user: id.username,
                    length: library.length
                })
        }}
        if (!arr.length) {
            msg.delete()
            return this.send_error(message, 1, `Everyone  has already been indexed`)
        }
        let num = 1
        msg.delete()
        let list = arr.map(a => `\`${num++}\` **[${a.user}](https://last.fm/user/${a.user})** updated with **${a.length}** artists`)
        this.db.delete(`IndexCheck_${message.guild.id}`)
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setTitle('Indexed Users')
            .setDescription(list.join('\n'))
            .setColor(this.hex)
            .setFooter(`Everyones playcounts and artists are up to date`)
        if (list.length <= 10) {
            return message.channel.send({ embeds: [embed] })
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}