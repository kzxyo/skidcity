const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')
module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'topalbums',
            aliases: ['tab'],
            type: client.types.LASTFM,
            usage: 'lastfm topalbums [user] [period]',
            description: 'View a list of your last.fm top played albums',
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
   
        const member = message.mentions.members.first() || message.member
        const {
            LastfmUsers,
        } = require('../../../utils/db.js')
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let recent
        let Artist
        if (member !== message.member) Artist = args.slice(1).join(' ')
        if (member === message.member) Artist = args.slice(0).join(' ')
        let check = await this.lastfm.artist_getinfo(user.username, Artist)
        let userinfo = await this.lastfm.user_getinfo(user.username)
        if (args.length === 0) {
            const data = await this.lastfm.user_getrecent(user.username)
            if (data.error) {
                return this.send_error(message, 1, `There was an error fetching info from **last.fm**`)
            } else {
                recent = data.recenttracks.track[0].artist[`#text`]
            }
        } else {
            recent = check.artist.name
        }
        var url = "http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=" + user.username + "&api_key=" + this.config.LASTFMKEY + "&format=json&limit=500";
        var options = {
            uri: url,
            json: true
        };
        var rp = require('request-promise');
        rp(options)
            .then(function (albums) {
                let num = 1
                let list = albums.topalbums.album.filter(a => a.artist.name.toLowerCase() === recent.toLowerCase()).map(a => `\`${num++}\` **[${a.name}](${a.url})** with **${a.playcount}** plays`)
                let is
                if (member === message.member) is = `${message.member} You dont have`
                if (member !== message.member) is = `${member} doesnt have`
                if (!list.length) {
                    const embed = new MessageEmbed()
                        .setDescription(`<:info:828536926603837441> ${is} any **Top Albums** for \`${recent}\``)
                        .setColor("#78c6fe");
                    return message.channel.send({ embeds: [embed] });
                }
                let profile_image = userinfo.user.image[3]['#text']
                const embed = new MessageEmbed()
                    .setTitle(`${user.username}'s Top Albums for '${recent}'`)
                    .setDescription(`${list.join('\n')}`)
                    .setColor(rColor)
                    .setThumbnail(profile_image)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setFooter(`Top albums: (artist)`, message.author.avatarURL({
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
                return this.send_error(message, 1, `an unexpected error occured while trying to get **Album Info**`)
            })
    }
}