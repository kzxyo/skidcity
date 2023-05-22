const { MessageEmbed } = require('discord.js');
const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'goal',
            type: client.types.LASTFM,
            usage: 'lastfm goal [number]',
            description: 'Set a goal for your last.fm scrobbles',
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
        const profile = await this.lastfm.user_getinfo(user.username)
        const goal = args[0]
        if(isNaN(args[0])) return this.send_error(message, 1, `Your goal must be a type of **number**`)
        if(parseInt(goal) < parseInt(profile.user.playcount)) return this.send_error(message, 1, `Your goal must be **greater** than your current scrobblecount`)
        if(parseInt(goal) === parseInt(profile.user.playcount)) return this.send_error(message, 1, `Your goal must be **greater** than your current scrobblecount`)
        this.db.set(`goal_${message.author.id}`, goal)
        return this.send_success(message, `Last.fm goal set to **${parseInt(goal).toLocaleString()}**: you need **${parseInt(goal) - parseInt(profile.user.playcount)}** more scrobbles to reach it`)
    }
}