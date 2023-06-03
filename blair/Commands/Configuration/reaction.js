const Commands = [ 'add' ]
const { parseEmoji } = require('discord.js'), { parse } = require('twemoji-parser')

const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class Reaction extends Command {
    constructor (Client) {
        super (Client, 'reaction', {
            Aliases : [ 'react' ],

            Syntax : 'reaction (Command)',
            Arguments : [ 'Command' ],
            
            Permissions : [ 'ManageGuild' ],

            Commands : [
                {
                    Name : 'reaction add',

                    About : 'Add a reaction trigger to the server.',
                    Syntax : 'reaction add (Emoji or Emote) (Trigger Word) [-previous]'
                },
                {
                    Name : 'reaction remove',
                    Aliases : [ 'delete', 'del' ],

                    About : 'Remove a reaction trigger from the server.',
                    Syntax : 'reaction remove (Emoji or Emote) (Trigger Word)'
                },
                {
                    Name : 'reaction view',
                    Aliases : [ 'list' ],

                    About : 'Check every reaction trigger in the server.',
                    Syntax : 'reaction view'
                }
            ],
            Module : 'Configuration'
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            return new Client.Help(
                Message, {
                    About : 'Reaction',
                    Syntax : 'reaction'
                }
            )
        }

        switch (Command) {
            case ('add') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            About : 'Reaction Add',
                            Syntax : 'reaction add'
                        }
                    )
                }

                try {
                    var Reaction
                    
                    const Emote = parseEmoji(Arguments[1])          
                    
                    if (Emote.id) {
                        const FetchEmote = await Client.emojis.cache.get(Emote.id)

                        if (!FetchEmote) {
                            return new Client.Response(
                                Message, `Couldn't find any **Shared Servers** with that emote. Maybe try a different emote?`
                            )
                        } else {
                            Reaction = { 
                                Emote : FetchEmote.id, 
                                Type : 'Emote' 
                            }
                        }
                    } else {
                        const Emoji = parse(Arguments[1], { 
                            assetType : 'png' 
                        })
                        
                        if (!Emoji[0]) {
                            return new Client.Response(
                                Message, `Couldn't find an **Emote** or **Emoji** in your arguments.`
                            )
                        } else {
                            Reaction = { 
                                Emote : Emoji[0].text, 
                                Type : 'Emoji' 
                            }
                        }
                    }
                    
                    if (!Arguments[2]) {
                        return new Client.Response(
                            Message, `Missing argument **Trigger**.`
                        )
                    }

                    Client.Database.query(`SELECT * FROM reactions WHERE guild_id = $1 AND trigger = $2 AND reaction = $3`, {
                        bind : [Message.guild.id, String(Arguments[2]).toLowerCase(), Reaction.Emote]
                    }).then(async ([Results]) => {
                        if (Results.length > 0) {
                            return new Client.Response(
                                Message, `Cannot add the same **Reaction** twice. `
                            )
                        }

                        Client.Database.query(`SELECT * FROM reactions WHERE guild_id = $1 AND trigger = $2`, {
                            bind : [Message.guild.id, String(Arguments[2]).toLowerCase()]
                        }).then(async ([Results]) => {
                            if (Results.length >= 3) {
                                return new Client.Response(
                                    Message, `Maximum amount of **Reactions** has been added for that trigger.`
                                )
                            }

                            Client.Database.query(`INSERT INTO reactions (guild_id, reaction, trigger, type, author) VALUES ($1, $2, $3, $4, $5)`, {
                                bind : [Message.guild.id, Reaction.Emote, String(Arguments[2]).toLowerCase(), Reaction.Type, Message.author.id]
                            }).then(async () => {
                                if (Reaction.Type === 'Emote') Reaction.Emote = await Client.emojis.cache.get(Reaction.Emote)

                                return new Client.Response(
                                    Message, `Added a **Reaction** for \`${String(Arguments[2]).toLowerCase()}\` with ${Reaction.Emote}`
                                )
                            })
                        })
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'reaction add', Error
                    )
                }

                break
            }
        }
    }
}