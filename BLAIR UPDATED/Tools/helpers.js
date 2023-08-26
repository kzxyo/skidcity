const Discord = require('discord.js')

module.exports = class Helpers {
    constructor (bot) {
        this.bot = bot
    }   

    async case () {
        const { moderator, target, reason = `No reason provided`, duration = null } = parameters

        const history = await this.bot.db.query('SELECT * FROM history WHERE guild_id = $1', { bind : [ message.guild.id ] }).then(([r]) => r)
        const num = history.length > 0 ? Math.max(...history.map((entry) => entry.case_id)) + 1 : 1

        const log = new Discord.EmbedBuilder({
            author : {
                name : 'Moderation Entry',
                iconURL : moderator.displayAvatarURL()
            },
            fields : [
                {
                    name : 'Information',
                    value : `**Case #${num}** | ${action}`
                }
            ]
        }).setColor(bot.colors.neutral)
    }
}