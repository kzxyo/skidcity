const Command = require('../Command.js');

module.exports = class Crownunban extends Command {
    constructor(client) {
        super(client, {
            name: 'crownunban',
            aliases: ['cunban'],
            type: client.types.LASTFM,
            usage: 'crownunban [user]',
            description: 'remove a users blacklist from getting crowns',
            userPermissions: ['MANAGE_GUILD', 'MANAGE_MESSAGES'],
            subcommands: ['crownunban']
        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        const {
            bans,
        } = require('../../utils/db.js')
        if (!args.length) {
            return this.help(message)
        }
        const user = this.functions.get_member(message, args.join(' '))
        if (!user) {
            return this.invalidUser(message)
        }
        const unbanned = await bans.destroy({
            where: {
                guildID: message.guild.id,
                userID: user.id
            }
        })
        if (unbanned) {
            return this.send_success(message, `**${user.user.tag}** is no longer crownbanned and will no longer be hidden from \`${prefix.prefix}lastfm whoknows\``)
        } else {
            return this.send_error(message, 1, `**${user.user.tag}** is not crown banned`)
        }
    }
}