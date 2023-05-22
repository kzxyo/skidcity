const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const AsciiTable = require('ascii-table')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'taste',
            aliases: ['compare'],
            type: client.types.LASTFM,
            usage: 'lastfm taste [member]',
            description: 'Compare another persons taste with your own',
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
        if (!args[0]) return this.send_error(message, 1, `You must **provide a user** to check the taste of`)
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
            for (const artist of artists) {
                const is = opp_artists.lib.find(a => a.name === artist.name)
                if (is) {
                    arr.push({
                        artist: artist.name,
                        plays: is.playcount,
                        author_plays: this.db.get(`Library_${message.author.id}`).lib.find(a => a.name === artist.name).playcount
                    })
                }
            }
            if (!arr.length) {
                return this.send_info(message, `You and **${member.user.username}** do not have any artists in common`)
            }
            let table = new AsciiTable('Taste comparison');
            table.setHeading('Artists', `Plays`)
            let sym
            for (const a of arr.slice(0, 10)) {
                if (parseInt(a.author_plays) > parseInt(a.plays)) sym = '>'
                if (parseInt(a.author_plays) < parseInt(a.plays)) sym = '<'
                if (parseInt(a.author_plays) === parseInt(a.plays)) sym = '='
                table.addRow(`${a.artist}`, `${a.author_plays} ${sym} ${a.plays}`);
            }
            const embed = new MessageEmbed()
                .setAuthor(message.author.tag, message.author.avatarURL({
                    dynamic: true
                }))
                .setTitle(`${check.username} vs ${user.username}`)
                .setColor(rColor)
                .setDescription(`
\`\`\`
${table}
\`\`\``)
                .setFooter(`${arr.length} total mutual artists`)
            message.channel.send({ embeds: [embed] })
        }
    }
}