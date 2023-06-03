const Command = require('../Command.js');

module.exports = class Crownban extends Command {
    constructor(client) {
        super(client, {
            name: 'crownban',
            aliases: ['cban'],
            type: client.types.LASTFM,
            usage: 'crownban [user]',
            description: 'Hide a user from `Lastfm whoknows` and stop them from getting crowns',
            userPermissions: ['MANAGE_GUILD', 'MANAGE_MESSAGES'],
            subcommands: ['crownban']
        });
    }
    async run(message, args) {
        const prefix = message.prefix
        const {
            bans,
            crowns
        } = require('../../utils/db.js')
        if (!args.length) {
            return this.help(message)
        }
        const user = this.functions.get_member(message, args.join(' '))
        if (!user) {
            return this.invalidUser(message)
        }
        try {
            await crowns.destroy({
                where: {
                    guildID: message.guild.id,
                    userID: user.id
                }
            })
            await bans.create({
                guildID: message.guild.id,
                userID: user.id
            })
                return this.send_success(message, `**${user.user.tag}** has been crownbanned and will be hidden from \`${prefix}lastfm whoknows\``)
        } catch (e) {
            if (e.name === 'SequelizeUniqueConstraintError') {
                return this.send_error(message, 1, `**${user.user.tag}** is already banned in here from getting crowns`)
            }
        }
    }
}