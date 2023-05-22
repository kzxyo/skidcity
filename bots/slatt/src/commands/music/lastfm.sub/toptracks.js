const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'toptracks',
            aliases: ['tt', 'ttt'],
            type: client.types.LASTFM,
            usage: 'lastfm toptracks [user]',
            description: 'View a list of your last.fm top played tracks',
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
        let Artist
        if (member !== message.member) Artist = args.slice(1).join(' ')
        if (member === message.member) Artist = args.slice(0).join(' ')
        let userinfo = await this.lastfm.user_getinfo(user.username)
        let recent
        let check = await this.lastfm.artist_getinfo(user.username, Artist)
        if (!args.length) {
            const data = await this.lastfm.user_getrecent(user.username)
            if (data.error) {
                return this.send_error(message, 1, `There was an error fetching info from **last.fm**`)
            } else {
                recent = data.recenttracks.track[0].artist[`#text`]
            }
        } else {
            recent = check.artist.name
        }
        var url = "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=" + user.username + "&api_key=" + this.config.LASTFMKEY + "&format=json&limit=500";
        var options = {
            uri: url,
            json: true
        };
        var rp = require('request-promise');
        rp(options)
            .then(function (tracks) {
                let num = 1
                let list = tracks.toptracks.track.filter(a => a.artist.name.toLowerCase() === recent.toLowerCase()).map(t => `\`${num++}\` **[${t.name}](${t.url})** with **${t.playcount}** plays`)
                let is
                if (member === message.member) is = `${message.member} You dont have`
                if (member !== message.member) is = `${member} doesnt have`
                if (!list.length) {
                    const embed = new MessageEmbed()
                        .setDescription(`<:info:828536926603837441> ${is} any **Top Tracks** for \`${recent}\``)
                        .setColor("#78c6fe");
                    return message.channel.send({ embeds: [embed] });
                }
                let profile_image = userinfo.user.image[3]['#text']
                const embed = new MessageEmbed()
                    .setTitle(`${user.username}'s Top Tracks for '${recent}'`)
                    .setDescription(`${list.join('\n')}`)
                    .setColor(rColor)
                    .setThumbnail(profile_image)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setFooter(`Top tracks: (artist)`, message.author.avatarURL({
                        dynamic: true
                    }))
                if (list.length <= 10) {
                    message.channel.send({ embeds: [embed] });
                } else {
                    return new ReactionMenu(message.client, message.channel, message.member, embed, list);
                }
            })
            .catch(err => {
                console.log(err)
                return this.send_error(message, 1, `an unexpected error occured while trying to get **Track Info**`)
            })
    }
}