const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'crowns',
            type: client.types.LASTFM,
            usage: 'lastfm crowns [member]',
            description: 'View a list of your last.fm crowns',
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
        const {
            crowns,
            LastfmUsers
        } = require('../../../utils/db.js');
        const user = this.functions.get_member_or_self(message, args.join(' '))
        if (!user) return this.invalidUser(message)
        const User = await LastfmUsers.findOne({
            where: {
                userID: user.id
            }
        })
        if (!User) {
            return this.link_lastfm(message, user)
        }
        const guildcrowns = await crowns.findAll({
            where: {
                guildID: message.guild.id,
                userID: user.id
            }
        })
        if (guildcrowns.length === 0) {
            await this.send_error(message, 1, `${user === message.member ? 'You have' : `**${user.user.username}** has`} no crowns in ${message.guild.name}, use \`${message.prefix}lastfm whoknows\` to claim crowns`)
            return
        }
        if (guildcrowns.length > 0) {
            let num = 0
            const description = guildcrowns.sort((a, b) => parseInt(b.artistPlays) - parseInt(a.artistPlays))
                .map(x => `\`${++num}\`. [${x.artistName}](https://last.fm/music/${x.artistName.replace(/`?\ `?/g, `+`)}) — **${x.artistPlays}** plays`)
            const embed = new MessageEmbed()
                .setAuthor(message.author.tag, message.author.avatarURL({
                    dynamic: true
                }))
                .setTitle(`Crowns for ${user.user.tag}`)
                .setDescription(description.join('\n'))
                .setThumbnail(user.user.avatarURL({
                    dynamic: true
                }))
                .setFooter(`${user === message.member ? 'You have' : `${user.user.username} has`} ${guildcrowns.length} crowns here`)
                .setColor(rColor)
            if (description.length <= 10) {
                message.channel.send({embeds: [embed]})
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, description);
            }
        }
    }
}