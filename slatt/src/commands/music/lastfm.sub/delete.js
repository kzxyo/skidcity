const Subcommand = require('../../Subcommand.js');


module.exports = class Delete extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'delete',
            aliases: ['remove'],
            type: client.types.LASTFM,
            usage: 'lastfm delete',
            description: 'Delete your last.fm username from the database',
        });
    }
    async run(message, args) {
        const {
            crowns,
            LastfmUsers,
        } = require('../../../utils/db.js');
        const amount = await LastfmUsers.destroy({
            where: {
                userID: message.author.id
            }
        })
        if (amount > 0) {
            await crowns.destroy({
                where: {
                    userID: message.author.id
                }
            })
            return this.send_success(message, `Your last.fm username was **unlinked**, and your crowns were deleted.`)
        } else {
            return this.link_lastfm(message, message.member)
        }
    }
}