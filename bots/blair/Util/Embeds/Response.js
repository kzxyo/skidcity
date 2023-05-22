const { EmbedBuilder } = require('discord.js')

module.exports = class Response {
    constructor (Message, Content, Options) {
        if (Options && Options.Reply) {
            Message.reply({
                embeds : [
                    new EmbedBuilder({
                        description : `${Content}`,
                    }).setColor(Message.client.Color)
                ],
                allowedMentions : {
                    repliedUser : false
                }
            })
        } else {
            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        description : `${Content}`,
                    }).setColor(Message.client.Color)
                ]
            })
        }
    }
}

