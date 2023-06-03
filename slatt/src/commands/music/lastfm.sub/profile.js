const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'profile',
            aliases: ['view'],
            type: client.types.LASTFM,
            usage: 'lastfm profile [user]',
            description: 'Display another members last.fm profile',
        });
    }
    async run(message, args) {
        message.channel.sendTyping()
   
        let member = message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ')) || message.mentions.members.first() || message.guild.members.cache.get(args.join(' ')) || message.guild.members.cache.find(x => x.user.username.toLowerCase() === args.join(' ') || x.user.username.toLowerCase() === args.join(' ')) || message.guild.members.cache.find(x => x.user.tag === args.join(' ') || x.user.tag === args.join(' '))
        if (!args[0]) member = message.member
        const {
            LastfmUsers,
        } = require('../../../utils/db.js')
        let user
        if (args[0] && member === undefined) user = args[0]
        if (member !== undefined) user = await LastfmUsers.findOne({
            where: {
                userID: member.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, member)
        }
        let recent = await this.lastfm.user_getrecent(user.username || user)
        let track = recent.recenttracks.track[0]
        let userInfo = await this.lastfm.user_getinfo(user.username || user);
        let lib = await this.db.get(`Library_${member ? member.id : null}`)
        const moment = require('moment');
        const date = moment().subtract(userInfo.user.registered['#text'], 'ms').format('dddd, MMMM Do YYYY')
        let Color
        let findcolor = await message.client.db.lf_color.findOne({ where: { userID: message.author.id } })
        if (findcolor !== null) { 
            Color = findcolor.color
        } else {
            Color = this.hex
        }
        const embed = new MessageEmbed()
            .setAuthor(message.member.user.tag, message.member.user.displayAvatarURL({
                dynamic: true
            }))
            .setThumbnail(userInfo.user.image[3]['#text'])
            .setColor(this.hex)
            .setTitle(`__${user.username || user}'s profile__`)
            .setURL(userInfo.user.url)
            .setDescription(`> <:helpLastfm:828537765636866108> **${member ? member.user.username : user}** Last listened to ${track ? `[${track.name}](${track.url})` : '**No track**'} by ${track ? `[${track.artist['#text']}](https://last.fm/music/${encodeURIComponent(track.artist['#text'])})` : '**No artist**'}`)
        if (lib) embed.addField(`Library Info`, `\`\`\`js
1. ${lib.lib[0].name} : ${lib.lib[0].playcount} plays
2. ${lib.lib[1].name} : ${lib.lib[1].playcount} plays
3. ${lib.lib[2].name} : ${lib.lib[2].playcount} plays\`\`\``)
        embed.addField(`**Total Scrobbles**`, `${userInfo.user.playcount}`)
        embed.addField(`**Registered**`, `${date}`)
        embed.addField(`**Color**`, `${Color}`)
        embed.setFooter(`${lib ? lib.lib.length : "No"} artists found in library`, 'https://tse3.mm.bing.net/th?id=OIP.2teGH-tBjztC6sn_0OrRhwHaHa&pid=Api&P=0&w=300&h=300')
        message.channel.send({ embeds: [embed] })
    }
}