const Subcommand = require('../../Subcommand.js');
const fetch = require('node-fetch')
const {
    stringify
} = require('querystring');
const { MessageEmbed } = require('discord.js')
module.exports = class Set extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'set',
            aliases: ['setname'],
            type: client.types.LASTFM,
            usage: 'lastfm set [lastfm_username]',
            description: 'Update your last.fm username',
        });
    }
    async run(message, args) {
        if (this.db.get(`lastfm_blacklisted_${message.author.id}`)) return message.channel.send('NO XD')
        const {
            crowns,
            LastfmUsers,
        } = require('../../../utils/db.js');
        if (!args.length) {
            return this.send_error(message, 1, `Provide a valid last.fm username link to your account`)
        }
        const user = await LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        const params = stringify({
            method: 'user.getinfo',
            api_key: this.config.LASTFMKEY,
            user: args[0],
            format: 'json'
        })
        const data = await fetch(`http://ws.audioscrobbler.com/2.0/?${params}`).then(r => r.json())
        if (data.user) {
            if (user) {
                const amount = await LastfmUsers.destroy({
                    where: {
                        userID: message.author.id
                    }
                })
                if (amount > 0) {
                    await crowns.destroy({
                        where: {
                            userID: message.author.id
                        }
                    })
                }
                const updating = new MessageEmbed().setDescription(`<:info:828536926603837441> ${message.author} Updating username from [${user.username}](https://last.fm/users/${user.username}) to [${data.user.name}](https://last.fm/users/${data.user.name})`).setColor("#78c6fe")
                const msg = await message.channel.send({ embeds: [updating] })
                await LastfmUsers.create({
                    userID: message.author.id,
                    username: data.user.name
                })
                let artist_info = await this.lastfm.user_getlibrary(data.user.name)
                const artists = artist_info.artists ? artist_info.artists.artist : []
                let track_info = await this.lastfm.get_toptracks(data.user.name)
                const tracks = track_info.toptracks ? track_info.toptracks.track : []
                let album_info = await this.lastfm.get_topalbums(data.user.name)
                const albums = album_info.topalbums ? album_info.topalbums.album : []
                if (artists.length) {
                    let a_a = []
                    for(const a of artists) {
                        a_a.push({
                            name: a.name,
                            playcount: a.playcount
                        })
                    }
                    this.db.set(`Library_${message.author.id}`, {
                        user: data.user.name,
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
                        user: data.user.name,
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
                        user: data.user.name,
                        lib: al_a
                    })
                }
                const em = new MessageEmbed().setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Your last.fm username was set to [${data.user.name}](https://last.fm/users/${data.user.name})`).setColor("#007f00")
                return msg.edit({ embeds: [em] })
            }
            const updating = new MessageEmbed().setDescription(`<:info:828536926603837441> ${message.author} updating your username, please wait...`).setColor("#78c6fe")
            const msg = await message.channel.send({ embeds: [updating] })
            await LastfmUsers.create({
                userID: message.author.id,
                username: data.user.name
            })
            let artist_info = await this.lastfm.user_getlibrary(data.user.name)
            const artists = artist_info.artists ? artist_info.artists.artist : []
            let track_info = await this.lastfm.get_toptracks(data.user.name)
            const tracks = track_info.toptracks ? track_info.toptracks.track : []
            let album_info = await this.lastfm.get_topalbums(data.user.name)
            const albums = album_info.topalbums ? album_info.topalbums.album : []
            if (artists.length) {
                let a_a = []
                for(const a of artists) {
                    a_a.push({
                        name: a.name,
                        playcount: a.playcount
                    })
                }
                this.db.set(`Library_${message.author.id}`, {
                    user: data.user.name,
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
                    user: data.user.name,
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
                    user: data.user.name,
                    lib: al_a
                })
            }
            const em = new MessageEmbed().setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Your last.fm username was set to [${data.user.name}](https://last.fm/users/${data.user.name})`).setColor("#007f00")
            msg.edit({ embeds: [em] })
        } else if (data.error === 6) {
            return this.send_error(message, 1, `**${args[0]}** is not a valid last.fm username`)
        }
    }
}