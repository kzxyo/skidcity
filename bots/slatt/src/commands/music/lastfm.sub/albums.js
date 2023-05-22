const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'albums',
            type: client.types.LASTFM,
            usage: 'lastfm albums [user]',
            description: 'View a list of your last.fm albums',
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
        const member = this.functions.get_member_or_self(message, args.join(' '))
        const user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let userinfo = await this.lastfm.user_getinfo(user.username)
        var url = "http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=" + user.username + "&api_key=" + this.config.LASTFMKEY + "&format=json&limit=100";
        var options = {
            uri: url,
            json: true
        };
        var rp = require('request-promise');
        rp(options)
            .then(function (albums) {
                let num = 1
                let list = albums.topalbums.album.map(a => `\`${num++}\` **[${a.name}](${a.url})** with **${a.playcount}** plays, by **${a.artist.name}**`)
                if (!list.length) {
                    const embed = new MessageEmbed()
                        .setDescription(`<:info:828536926603837441> ${message.author} You dont have any **Top Albums**`)
                        .setColor("#78c6fe");
                    return message.channel.send({ embeds: [embed] });
                }
                let profile_image = userinfo.user.image[3]['#text']
                const embed = new MessageEmbed()
                    .setTitle(`${user.username}'s Albums`)
                    .setDescription(`${list.join('\n')}`)
                    .setColor(rColor)
                    .setThumbnail(profile_image)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setFooter(`Top albums: ${list.length}`, message.author.avatarURL({
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