const Subcommand = require('../../Subcommand.js');
const ReactionMenu = require('../../ReactionMenu.js');
const {
    MessageEmbed
} = require('discord.js');
module.exports = class Claim extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'claim',
            type: client.types.LASTFM,
            usage: 'lastfm claim',
            description: 'Claim all available crowns',
        });
    }
    async run(message, args) {
        const user = await message.client.db.LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        if (user === null) {
            return this.link_lastfm(message, message.author)
        }
        const banned = await message.client.db.bans.findOne({
            where: {
                guildID: message.guild.id,
                userID: message.author.id
            }
        })
        if (banned) return this.send_error(message, 1, `You cant claim crowns. You have been **crown-banned**`)
        const lib = this.db.get(`Library_${message.author.id}`)
        if (!lib || !lib.lib.length) return this.send_error(message, 1, `Your **Last.fm library** wasnt formed properly. Use \`${message.prefix}lastfm reload\``)
        const Artists = lib.lib
        const arr = []
        const claiming = new MessageEmbed()
            .setDescription(`<:server:828538650757169152> ${message.author} Attempting to claim all **available** crowns.. Please wait.`)
            .setColor('2196f3')
        const msg = await message.channel.send({embeds: [claiming]})
        for (const artist of Artists) {
            const crown = await message.client.db.crowns.findOne({
                where: {
                    guildID: message.guild.id,
                    artistName: artist.name
                }
            })
            if (crown && !message.guild.members.cache.get(crown.userID) || crown && parseInt(crown.artistPlays) < parseInt(artist.playcount) || !crown) {
                if (parseInt(artist.playcount) > 5) {
                    if (!crown) {
                        await message.client.db.crowns.create({
                            guildID: message.guild.id,
                            userID: message.author.id,
                            artistName: artist.name,
                            artistPlays: artist.playcount
                        })
                    } else {
                        await message.client.db.crowns.update({
                            userID: message.author.id,
                            artistPlays: artist.playcount
                        }, {
                            where: {
                                guildID: message.guild.id,
                                artistName: artist.name,
                            }
                        })
                    }
                    arr.push({ artist: artist.name, plays: artist.playcount })
                }
            }
        }
        let num = 1
        const list = arr.map(x => `\`${num++}\` **[${x.artist}](https://last.fm/music/${encodeURIComponent(x.artist.replace('+', ''))})** - ${x.plays} plays`)
        msg.delete()
        if (!list.length) return this.send_error(message, 1, `There werent any available crowns to claim. **You must have over 5 plays for the artist to quick-claim**`)
        msg.delete()
        const embed = new MessageEmbed()
            .setTitle('Claimed crowns')
            .setAuthor(message.author.tag, message.author.displayAvatarURL({
                dynamic: true
            }))
            .setFooter(`${list.length} total claimed crowns`)
            .setDescription(list.join('\n'))
            .setColor(this.hex);
        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] });
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}