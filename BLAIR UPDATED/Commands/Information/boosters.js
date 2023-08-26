const Command = require('../../Structures/Base/command.js')

module.exports = class Boosters extends Command {
    constructor (bot) {
        super (bot, 'boosters', {
            description : 'View all server boosters',
            aliases : [ 'boosts' ],
            commands : [
                {
                    name : 'boosters lost',
                    description : 'View all members which are no longer boosting'
                }
            ],
            module : 'Information'
        })
    }
}