const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class Ping extends Command {
    constructor (Client) {
        super (
            Client, 'ping', {
                Aliases : [ 'latency', 'ms' ]
            }
        )
    }

    async Invoke (Client, Message, Arguments) {
        console.log(Client)
        const PingMessage = await Message.channel.send({
            embeds : [
                new EmbedBuilder({
                    description : `Websocket: **${Client.ws.ping}ms**`
                }).setColor('#c6bfc6')
            ]
        })

        const TimeDifference = (PingMessage.editedAt || PingMessage.createdAt) - (Message.editedAt || Message.createdAt)

        PingMessage.edit({
            embeds : [
                new EmbedBuilder({
                    description : `Websocket: **${Client.ws.ping}ms** (edit: **${TimeDifference - Client.ws.ping.toFixed(1)}ms**)`
                }).setColor('#c6bfc6')
            ]
        })
    }
}