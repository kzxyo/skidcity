const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require("discord.js")
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'whoknowsalbum',
            aliases: ['wka'],
            type: client.types.LASTFM,
            usage: 'lastfm whoknowsalbum [album]',
            description: 'Who knows a album in your server',
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
        let albumName
        if (!args.length) {
            const data = await this.lastfm.user_getrecent(user.username)
            if (data.error) {
                return this.send_error(message, 1, `There was an error fetching info from **last.fm**`)
            } else {
                albumName = data.recenttracks.track[0].album[`#text`] + " " + data.recenttracks.track[0].artist[`#text`]
            }
        } else {
            albumName = args.join(` `)
        }
        let data = await this.lastfm.album_search(albumName)
        if (data.error === 6) {
            await this.send_error(message, 1, `There was no result for **${albumName}** on last.fm`)
            return
        } else {
            let know = []
            const user = await LastfmUsers.findAll()
            for (const users of user) {
                const member = message.guild.members.cache.get(users.userID)
                if (member) {
                const user = this.db.get(`Albums_${member.id}`)
                if (!user) {
                    continue
                }
                let albumData
                if (user && user.lib && user.lib.length) albumData = user.lib.find(a => a.name.toLowerCase() === data.results.albummatches.album[0].name.toLowerCase())
                if (!albumData) continue
                let plays = albumData.playcount
                know.push({
                    member: member.user,
                    user: user.user,
                    plays: plays
                })
            }
            }
            if (know.length === 0) {
                await this.send_error(message, 1, `There are no listeners for **${data.results.albummatches.album[0].name}** here, if you havent already, use \`${prefix.prefix}lastfm reload\``)
                return
            }
            know = know.sort((a, b) => parseInt(b.plays) - parseInt(a.plays))
            let num = 0
            const AlbumName = data.results.albummatches.album[0].name.length > 20 ? data.results.albummatches.album[0].name.slice(0, 20) + '...' : data.results.albummatches.album[0].name
            const description = know
                .map(x => `\`${++num}\` [${x.member.username}#${x.member.discriminator}](https://last.fm/user${x.user}) — **${parseInt(x.plays).toLocaleString()}** plays`)
            let rank = know.map(k => k.member.id).indexOf(message.author.id)
            const embed = new MessageEmbed()
            embed.setTitle(`Who knows ${AlbumName} in ${message.guild.name}?`)
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