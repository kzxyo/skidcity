const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'recent',
            aliases: ['recentracks', 'recentlyplayed'],
            type: client.types.LASTFM,
            usage: 'lastfm recent [user]',
            description: 'View a list of your recently played last.fm tracks',
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
        const {
            LastfmUsers,
        } = require('../../../utils/db.js');
        const member = message.mentions.members.first() || message.member
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let userinfo = await this.lastfm.user_getinfo(user.username)
        var url = "http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=" + user.username + "&api_key=" + this.config.LASTFMKEY + "&format=json";
        var options = {
            uri: url,
            json: true
        };
        let which
        if (message.mentions.members.first()) which = args.slice(1).join(' ')
        if (!message.mentions.members.first()) which = args.slice(0).join(' ')
        let artist_paramater = this.functions.paramater('artist', which)
        var rp = require('request-promise');
        rp(options)
            .then(tracks => {
                let num = 0
                let list
                let title
                if (artist_paramater.length < 2) {
                    title = `${user.username}'s recent tracks`
                    list = tracks.recenttracks.track.map(t => `\`${++num}\`. ` + "**[" + t.name + "](" + t.url + ")**" + " by **" + t.artist['#text'] + "**")
                }
                if (artist_paramater.length > 1) {
                    title = `${user.username}'s recent tracks ${`for '${artist_paramater[1].replace(/^\s+/g, '').toLowerCase()}'`}`

                    list = tracks.recenttracks.track.filter(a => a.artist['#text'].toLowerCase() === artist_paramater[1].replace(/^\s+/g, '').toLowerCase()).map(t => `\`${++num}\`. ` + "**[" + t.name + "](" + t.url + ")**" + " by **" + t.artist['#text'] + "**")
                }
                if (!list.length) return this.send_error(message, 1, `If you suplied an artist, you have no **recent tracks** for them, otherwise your **last.fm** is showing no info`)
                let profile_image = userinfo.user.image[3]['#text']
                const embed = new MessageEmbed()
                    .setTitle(title)
                    .setDescription(`${list.join('\n')}`)
                    .setColor(rColor)
                    .setThumbnail(profile_image)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setFooter(message.author.tag, message.author.avatarURL({
                        dynamic: true
                    }))
                if (list.length <= 10) {
                    message.channel.send({ embeds: [embed] });
                } else {
                    return new ReactionMenu(message.client, message.channel, message.member, embed, list);
                }
            }).catch(err => {
                message.client.logger.error(err)
                return this.send_error(message, 1, `an unexpected error occured while trying to get **recent tracks**`)
            })
    }
}