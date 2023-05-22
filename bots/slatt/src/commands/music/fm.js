const {
    MessageEmbed
} = require('discord.js');
const embedbuilder = require('godembed')
const Command = require('../Command.js');

module.exports = class EvalCommand extends Command {
    constructor(client) {
        super(client, {
            name: "fm",
            aliases: ['nowplaying', 'np'],
            subcommands: ['fm'],
            usage: 'fm [user]',
            type: client.types.LASTFM,
            description: "Shows yours or the user you provided's currently song playing on last.fm",
        });

    }
    async run(message, args) {
        if(message.client.subcommands.get(`lastfm ${args[0]}`) || message.client.subcommand_aliases.get(`lastfm ${args[0]}`)) return message.channel.send(`No. use ${message.prefix}lastfm ${args[0]}`)
        const ms = require("parse-ms");
        let rColor
        let findcolor = await message.client.db.lf_color.findOne({ where: { userID: message.author.id } })
        if (findcolor !== null) {
            rColor = findcolor.color
        } else {
            rColor = this.hex
        }
        let con = await message.client.db.embed.findOne({ where: { userID: message.author.id } })
        const member = this.functions.get_member_or_self(message, args.join(' '))
        if (!member) return this.invalidUser(message)
        const {
            LastfmUsers,
        } = require('../../utils/db.js');
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }

        let recent = await this.lastfm.user_getrecent(user.username)
        if (!recent.recenttracks) return this.api_error(message, `Last.fm`, 'your Last.fm profile returned no recent tracks')
        if (recent.recenttracks.track[0] === undefined) return this.api_error(message, `Last.fm`, 'Last.fm profile returned insufficient info')
        let track = recent.recenttracks.track[0]
        let album = recent.recenttracks.track[0]
            ? recent.recenttracks.track[0].album['#text'].length > 30
                ? recent.recenttracks.track[0].album['#text'].slice(0, 30) + '...'
                : recent.recenttracks.track[0].album['#text'] : '**None**'

        let artist = recent.recenttracks.track[0]
            ? recent.recenttracks.track[0].artist['#text'].length > 30
                ? recent.recenttracks.track[0].artist['#text'].slice(0, 30) + '...'
                : recent.recenttracks.track[0].artist['#text']
            : '**None**'
        let track_image = recent.recenttracks.track[0].image[3]["#text"]
        let info = await this.lastfm.user_getinfo(user.username)
        let total = info.user.playcount
        let profile_image = info.user.image[3]['#text']
        let artist_plays = await this.lastfm.artist_getinfo(user.username, artist)
        if(artist_plays.artist) artist_plays = artist_plays.artist.stats.userplaycount
        else artist_plays = '00'
        let track_plays = await this.lastfm.track_getinfo(user.username, artist, track.name) 
        if(track_plays.track) track_plays = track_plays.track.userplaycount
        else track_plays = '00'
        let np
        let ago
        if (!recent.recenttracks.track[0]['@attr']) {
            np = 'recently played'
            ago = ms((Date.now() - recent.recenttracks.track[0].date.uts * 1000));
        }
        if (recent.recenttracks.track[0]['@attr']) np = 'now playing';
        if (ago !== undefined) {
            if (ago.days !== 0) {
                ago = `· ${ago.days} days ago`
            } else if (ago.hours !== 0) {
                ago = `· ${ago.hours} hours ago`
            } else if (ago.minutes !== 0) {
                ago = `· ${ago.minutes} minutes ago`
            } else {
                ago = `· ${ago.seconds} seconds go`
            }
        } else {
            ago = `· ${parseInt(total).toLocaleString()} total`
        }
        if (con === null) {
            const embed = new MessageEmbed()
                .setAuthor(`${user.username} · ${np}`, profile_image)
                .setDescription(`
    > **track:** [${track.name.length > 30 ? track.name.slice(0, 30) + '...' : track.name}](${track.url})
    > **artist:** [${artist}](https://last.fm/music/${this.lastfm.artist_url(artist)})
    > **album:** [${album}](https://last.fm/music/${this.lastfm.album_url(artist, album)})`)
                .setFooter(`track plays: ${parseInt(track_plays).toLocaleString()} · artist plays: ${parseInt(artist_plays).toLocaleString()} ${ago}`)
                .setColor(rColor)
                .setThumbnail(track_image)
            return message.channel.send({ embeds: [embed] }).then(em => {
                if(artist === '$uicideboy$' || artist.toLowerCase() === 'lucki') {
                    em.react('<:fire2:921941738787069972>'); em.react('<:fire2:874532917970354216>')
                } else {
                    em.react('👍')
                    em.react('👎')
                } 
            });
        } else {
            const content = message.client.utils.replace_fm_variables(con.code, track, artist, album, np, profile_image, artist_plays, track_plays, user, track_image, total)
            let {
                embed,
            } = embedbuilder(message.client.utils.replace_all_variables(content, message, member))
            message.channel.send({
                embeds: [embed]
            }).then(embedMessage => {
                embedMessage.react("👍").then(embedMessage.react("👎"))
            })
        }
    }
}