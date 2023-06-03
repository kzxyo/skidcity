const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'topartists',
            aliases: ['tar'],
            type: client.types.LASTFM,
            usage: 'lastfm topartists [user] [period]',
            description: 'View a list of your last.fm top played artists',
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
        message.channel.sendTyping()
        const {
            LastfmUsers,
        } = require('../../../utils/db.js')
        let member = this.functions.get_member_or_self(message, args[0])
        if(!member) member = message.member
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let userinfo = await this.lastfm.user_getinfo(user.username)
        let period
        if(!args.length || member === message.member) period = args[0]
        else period = args[1]
        if (period === '7day' || period === '7d' || period === 'week' || period === '7days') {
            period = '7day'
        } else if (period == '1month' || period == '1m' || period == '30d' || period == '30days' || period == '30day' || period == 'month') {
            period = "1month"
        } else if (period == '3months' || period == '3m' || period == '3month') {
            period = "3month"
        } else if (period == '6month' || period == '6m' || period === '6months') {
            period = "6month"
        } else if (period == '12month' || period == '12m' || period == '12months' || period === '365d' || period === 'year') {
            period = "12month"
        } else {
            period = "Overall"
        }
        var rp = require('request-promise')
        var url = `http://ws.audioscrobbler.com/2.0/?method=user.gettopArtists&user=${user.username}&api_key=${this.config.LASTFMKEY}&format=json&period=${period}`
        var options = {
            uri: url,
            json: true
        };
        rp(options)
            .then(function (artists) {
                let num = 0
                let list = artists.topartists.artist.map(t => `\`${++num}\`. ` + "**[" + t.name + "](" + t.url + ")** **" + t.playcount + "** plays")
                let is
                if (member !== message.member) is = `${member} Does not have any`
                if (member === message.member) is = `${message.member} You dont have any`
                if (!list.length) {
                    const embed = new MessageEmbed()
                        .setDescription(`<:info:828536926603837441> ${is} top artists for period **${period}**`)
                        .setColor("#78c6fe");
                    return message.channel.send({ embeds: [embed] });
                }
                let profile_image = userinfo.user.image[3]['#text']
                const embed = new MessageEmbed()
                    .setTitle(`${user.username}'s Top Artists`)
                    .setDescription(`${list.join('\n')}`)
                    .setColor(rColor)
                    .setThumbnail(profile_image)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setFooter(message.author.tag + ` Period: (${period})`, message.author.avatarURL({
                        dynamic: true
                    }))
                if (list.length <= 10) {
                    message.channel.send({embeds: [embed]});
                } else {
                    return new ReactionMenu(message.client, message.channel, message.member, embed, list);
                }
            })
            .catch(err => {
                console.log(err)
                return this.send_error(message, 1, `an unexpected error occured while trying to get **Artist Info**`)
            })
    }
}