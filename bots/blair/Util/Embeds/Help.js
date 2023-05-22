const { EmbedBuilder } = require('discord.js')

module.exports = class Help {
    constructor (Message, Object) {
        if (Object) {
            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        author : {
                            name : `${Object.Syntax ? `.${Object.Syntax}` : 'No syntax was provided for this command.'}`,
                            url : 'https://blair.win/commands'
                        },
                        description : Object.About ? String(Object.About) : null
                    }).setColor(Message.client.Color)
                ]
            })
        } 
    }
}