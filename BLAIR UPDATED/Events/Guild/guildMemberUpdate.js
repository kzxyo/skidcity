const Event = require('../../Structures/Base/event.js')

module.exports = class GuildMemberUpdate extends Event {
    constructor (bot) {
        super (bot, 'guildMemberUpdate')
    }

    async execute (bot, oldMember, newMember) {
        try {
            if (oldMember.partial) {
                oldMember = oldMember.fetch()
            }

            if (newMember.partial) {
                newMember = newMember.fetch()
            }

            if (oldMember.premiumSince && !newMember.premiumSince) {
                bot.db.query('INSERT INTO boosters_lost (guild_id, user_id, started, stopped) VALUES ($1, $2, $3)', {
                    bind : [
                        newMember.guild.id, newMember.id, oldMember.premiumSince, new Date()
                    ]
                })
            }
        } catch (error) {
            return console.log('GuildMemberUpdate', error)
        }
    }
}