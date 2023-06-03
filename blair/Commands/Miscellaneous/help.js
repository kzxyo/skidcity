const Command = require('../../Structures/Base/Command.js')


const { EmbedBuilder, ActionRowBuilder, ButtonBuilder } = require('discord.js')

module.exports = class Help extends Command {
    constructor (Client) {
        super (Client, 'help', {
            Aliases : [ 'h' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        try {
            if (Arguments[0]) {
                Message.channel.send({
                    embeds : [
                        new EmbedBuilder({
                            author : {
                                name : 'Command Information: lastfm',
                                iconURL : 'https://blair.win/cdn/images/icon.png'
                            },
                            description : 'Interact with the Last.FM website through commands.',
                            fields : [
                                {
                                    name : 'General Syntax',
                                    value : '@blair#1006 lastfm (Command)'
                                },
                                {
                                    name : 'Aliases',
                                    value : 'lf, lfm',
                                    inline : true
                                },
                                {
                                    name : 'Arguments',
                                    value : 'Command',
                                    inline : true
                                },
                                {
                                    name : 'Permissions',
                                    value : 'None',
                                    inline : true
                                },
                                {
                                    name : 'Commands (2)',
                                    value : '.lastfm set - Set your Last.FM username to acce..\n.lastfm profile - Check a Last.FM user profile.',
                                    inline : true
                                }
                            ],
                            footer : {
                                text : 'Page 1/1 (1 entry) ∙ Last.FM Integration'
                            }
                        }).setColor(Client.Color)
                    ]
                })
            } else {
                Message.reply({
                    components : [
                        new ActionRowBuilder().addComponents(
                            new ButtonBuilder({
                                label : 'Commands',
                                url : 'https://blair.win/commands/'
                            }).setStyle('Link'),
                            new ButtonBuilder({
                                label : 'Documentation',
                                url : 'https://docs.blair.win/'
                            }).setStyle('Link')
                        )
                    ],
                    allowedMentions : {
                        repliedUser : false
                    }
                })
            }
        } catch (Error) {
            return console.error(Error)
        }
    }
}