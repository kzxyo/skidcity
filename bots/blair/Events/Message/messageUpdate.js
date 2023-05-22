const Event = require('../../Structures/Base/Event.js')

module.exports = class MessageUpdate extends Event {
    constructor (Client) {
        super (Client, 'messageUpdate')
    }

    async Invoke (oldMessage, newMessage) {
        const Structure = new this.Client.Structure(this.Client)

        Structure.Invoke(newMessage)
    }
}