const Event = require('../../Structures/Base/Event.js')

module.exports = class MessageReactionAdd extends Event {
    constructor (Client) {
        super (Client, 'messageReactionAdd')
    }

    async Invoke () {

    }
}