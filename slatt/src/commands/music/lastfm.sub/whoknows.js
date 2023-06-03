const { MessageEmbed } = require('discord.js');
const Subcommand = require('../../Subcommand.js');
module.exports = class Whoknows extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'whoknows',
            aliases: ['wk'],
            type: client.types.LASTFM,
            usage: 'lastfm whoknows [artist]',
            description: 'View a list of who listens to an artist',
        });
    }
    async run(message, args) {
        let rColor
        let findcolor = await message.client.db.lf_color.findOne({ where: { userID: message.author.id } })
        if (findcolor !== null) { 
            rColor = findcolor.color
        } else {
            rColor = this.hex
        }
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        message.channel.sendTyping()
        const {
            bans,
            LastfmUsers,
            crowns
        } = require('../../../utils/db.js');
        const user = await LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, message.author)
        }
        let artistName
        if (!args.length) {
            const data = await this.lastfm.user_getrecent(user.username)
            if (data.error) {
                return this.send_error(message, 1, `There was an error fetching info from **last.fm**`)
            } else {
                artistName = data.recenttracks.track[0].artist[`#text`]
            }
        } else {
            artistName = args.join(` `)
        }
        let data = await this.lastfm.artist_getinfo(user.username, artistName)
        if (data.error === 6) {
            await this.send_error(message, 1, `There was no result for **${artistName}** on last.fm`)
            return
        } else {
            let correction = await this.lastfm.artist_getCorrection(artistName)
            let actual_artist
            if (correction.corrections.correction) actual_artist = correction.corrections.correction.artist.name
            let know = []
            const user = await LastfmUsers.findAll()
            for (const users of user) {
                const member = message.guild.members.cache.get(users.userID)
                if (member) {
                    const user = this.db.get(`Library_${member.id}`)
                    if (!user) {
                        continue
                    }
                    let artistData
                    if (user && user.lib && user.lib.length) artistData = user.lib.find(a => a.name.toLowerCase() === actual_artist.toLowerCase())
                    if (!artistData) continue
                    let plays = artistData.playcount
                    const banned = await bans.findOne({
                        where: {
                            guildID: message.guild.id,
                            userID: member.user.id
                        }
                    })
                    if (!banned) {
                        know.push({
                            member: member.user,
                            user: user.user,
                            plays: plays
                        })
                    }
                }
            }
            if (know.length === 0) {
                await this.send_error(message, 1, `There are no listeners for **${data.artist.name}** here, if you havent already, use \`${prefix.prefix}lastfm reload\``)
                return
            }
            know = know.sort((a, b) => parseInt(b.plays) - parseInt(a.plays))
            const sorted = know[0]
            let num = 0
            const description = know
                .map(x => `\`${++num}\` [${x.member.username}#${x.member.discriminator}](https://last.fm/user/${x.user}) — **${parseInt(x.plays).toLocaleString()}** plays`)
            let rank = know.map(k => k.member.id).indexOf(message.author.id)
            const embed = new MessageEmbed()
            embed.setTitle(`Who knows ${data.artist.name} in ${message.guild.name}?`)
                .setAuthor(`${message.author.tag}`, message.author.displayAvatarURL({
                    dynamic: true
                }))
            embed.setThumbnail(message.guild.iconURL({dynamic:true}))
            embed.setColor(rColor)
            embed.setFooter(`You can use ${prefix.prefix}lastfm reload to update your plays\n${(await message.client.db.LastfmUsers.findAll()).filter(x => message.guild.members.cache.get(x.userID)).length} users have their last.fm linked here`)
            embed.setDescription(`${description.join('\n').replace('`1`', ':crown:').replace(message.author.tag, `**[${message.author.tag}](https://last.fm/user/${user.username})**`)}\nYou are rank \`#${rank + 1}\` out of \`${know.length}\` listeners`)
            const wkpgn = require('../../wkpgn.js')
            if (know.length <= 10) {
                message.channel.send({ embeds: [embed] })
            } else {
                new wkpgn(message.client, message.channel, message.author, user.username, rank, embed, description);
            }
            const old_crown = await crowns.findOne({
                where: {
                    guildID: message.guild.id,
                    artistName: actual_artist
                }
            })
            try {
                const banned = await bans.findOne({
                    where: {
                        guildID: message.guild.id,
                        userID: sorted.member.id
                    }
                })
                if (!banned) {
                    await crowns.create({
                        guildID: message.guild.id,
                        userID: sorted.member.id,
                        artistName: actual_artist,
                        artistPlays: sorted.plays
                    })
                }
            } catch (e) {
                if (e.name === 'SequelizeUniqueConstraintError') {
                    const crown = await crowns.findOne({
                        where: {
                            guildID: message.guild.id,
                            artistName: actual_artist
                        }
                    })
                    if (parseInt(crown.artistPlays) < parseInt(sorted.plays) || !message.guild.members.cache.has(crown.userID)) {
                        await crowns.update({
                            userID: sorted.member.id,
                            artistPlays: sorted.plays
                        }, {
                            where: {
                                guildID: message.guild.id,
                                artistName: actual_artist
                            }
                        })
                    }
                }
            }
            const new_crown = await crowns.findOne({
                where: {
                    guildID: message.guild.id,
                    artistName: actual_artist
                }
            })
            if(!old_crown || old_crown && new_crown && old_crown.userID !== new_crown.userID) {
                const claimed = new MessageEmbed().setColor(rColor).setDescription(`**${sorted.member.tag}** takes the crown for **${actual_artist}** with \`${sorted.plays}\` plays`)
                message.channel.send({embeds: [claimed]})
            }
        }
    }
}