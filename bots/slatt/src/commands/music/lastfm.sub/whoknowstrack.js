const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require("discord.js")
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'whoknowstrack',
            aliases: ['wkt'],
            type: client.types.LASTFM,
            usage: 'lastfm whoknowstrack [album]',
            description: 'Who knows a track in your server',
        });
    }
    async run(message, args) {
        message.channel.sendTyping()
   
        let rColor
        let findcolor = await message.client.db.lf_color.findOne({ where: { userID: message.author.id } })
        if (findcolor !== null) { 
            rColor = findcolor.color
        } else {
            rColor = this.hex
        }
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
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
        let trackName
        if (!args.length) {
            const data = await this.lastfm.user_getrecent(user.username)
            if (data.error) {
                return this.send_error(message, 1, `There was an error fetching info from **last.fm**`)
            } else {
                trackName = data.recenttracks.track[0].name + " " + data.recenttracks.track[0].artist[`#text`]
            }
        } else {
            trackName = args.join(` `)
        }
        let data = await this.lastfm.track_search(trackName)
        if (!data.results.trackmatches.track.length) {
            await this.send_error(message, 1, `There was no result for **${trackName}** on last.fm`)
            return
        } else {
            let know = []
            const user = await LastfmUsers.findAll()
            for (const users of user) {
                const member = message.guild.members.cache.get(users.userID)
                if (member) {
                    const user = this.db.get(`Tracks_${member.id}`)
                    if (!user) {
                        continue
                    }
                    let trackData
                    if (user && user.lib && user.lib.length) trackData = user.lib.find(t => t.name.toLowerCase() === data.results.trackmatches.track[0].name.toLowerCase())
                    if (!trackData) continue
                    let plays = trackData.playcount
                    know.push({
                        member: member.user,
                        user: user.user,
                        plays: plays
                    })
                }
            }
            if (know.length === 0) {
                await this.send_error(message, 1, `There are no listeners for **${data.results.trackmatches.track[0].name}** here, if you havent already, use \`${prefix.prefix}lastfm reload\``)
                return
            }
            know = know.sort((a, b) => parseInt(b.plays) - parseInt(a.plays))
            let num = 0
            const TrackName = data.results.trackmatches.track[0].name.length > 20 ? data.results.trackmatches.track[0].name.slice(0, 20) + '...' : data.results.trackmatches.track[0].name
            const description = know
                .map(x => `\`${++num}\` [${x.member.username}#${x.member.discriminator}](https://last.fm/user${x.user}) — **${parseInt(x.plays).toLocaleString()}** plays`)
            let rank = know.map(k => k.member.id).indexOf(message.author.id)
            const embed = new MessageEmbed()
            embed.setTitle(`Who knows ${TrackName} in ${message.guild.name}?`)
                .setAuthor(`${message.author.tag}`, message.author.displayAvatarURL({
                    dynamic: true
                }))
            embed.setThumbnail(message.guild.iconURL({
                dynamic: true
            }))
            embed.setColor(rColor)
            embed.setFooter(`You can use ${prefix.prefix}lastfm reload to update your plays\n${(await message.client.db.LastfmUsers.findAll()).filter(x => message.guild.members.cache.get(x.userID)).length} users have their last.fm linked here`)
            embed.setDescription(`${description.join('\n').replace(message.author.tag, `**[${message.author.tag}](https://last.fm/user/${user.username})**`)}\nYou are rank \`#${rank + 1}\` out of \`${know.length}\` listeners`)
            if (know.length <= 10) {
                message.channel.send({ embeds: [embed] })
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, description);
            }
        }
    }
}