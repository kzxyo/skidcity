const { MessageEmbed } = require('discord.js');
const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'progress',
            type: client.types.LASTFM,
            usage: 'lastfm progress',
            description: 'Progress report to track your Last.fm goal',
        });
    }
    async run(message, args) {
        const user = await message.client.db.LastfmUsers.findOne({
            where: {
                userID: message.author.id
            }
        })
        if (!user) {
            return this.link_lastfm(message, message.member)
        }
        const progress = require('string-progressbar')
        const profile = await this.lastfm.user_getinfo(user.username)
        const goal = this.db.get(`goal_${message.author.id}`)
        if(!goal) return this.send_error(message, 1, `You havent set a goal yet, use **${message.prefix}lastfm goal**`)
        const embed = new MessageEmbed()
        .setAuthor(user.username, profile.user.image[0]['#text'])
        .setTitle(`Last.fm progress`)
        .addField(`Goal`,  parseInt(goal).toLocaleString(), true)
        .addField(`Current`, parseInt(profile.user.playcount).toLocaleString(), true)
        .addField(`Plays needed`, (parseInt(goal) - parseInt(profile.user.playcount)).toLocaleString(), true)
        .addField(`Progress bar`, progress.filledBar(parseInt(goal), parseInt(profile.user.playcount), [15]).join(' ')+'%', true)
        .setColor(this.hex)
        message.channel.send({ embeds: [embed] })
    }
}