const Command = require('../../Structures/Base/Command.js')

module.exports = class Sequelize extends Command {
    constructor (Client) {
        super (Client, 'sequelize', {
            Aliases : [ 'sql' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (Message.author.id === '944099356678717500') {
            if (!Arguments[0]) return

            try {
                Client.Database.query(Arguments.join(' ')).then(async ([Results]) => {
                    await Message.react('✅')
                    console.log(Results)
                })
            } catch (Error) {
                return new Client.Error(
                    Message, 'sequelize', Error
                )
            }
        }
    }
}