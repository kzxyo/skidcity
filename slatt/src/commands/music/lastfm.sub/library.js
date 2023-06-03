const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'library',
            aliases: ['lib'],
            type: client.types.LASTFM,
            usage: 'lastfm library [user]',
            description: 'View a list of your library artists stored within slatt',
        });
    }
    async run(message, args) {
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
        let num = 1
        let lib = this.db.get(`Library_${member.id}`)
        if (!lib.lib.length) {
            return this.send_error(message, 1, `There were **no artists** found in ${member}'s library`)
        }
        let artists = lib.lib.map(a => `\`${num++}\` [${a.name}](https://last.fm/music/${encodeURIComponent(a.name)}) : **${a.playcount}** plays`)
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setColor(this.hex)
            .setTitle(`Artists for ${user.username}`)
            .setURL(`https://last.fm/user/${user.username}`)
            .setThumbnail(message.author.avatarURL({
                dynamic: true
            }))
            .setDescription(artists.join('\n'))
            .setFooter(`${artists.length} artists found`)
        if (artists.length <= 10) {
            message.channel.send({ embeds: [embed] })
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, artists);
        }
    }
}