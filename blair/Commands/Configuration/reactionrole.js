const Commands = [ 'add', 'remove' ]

const Command = require('../../Structures/Base/Command.js')

module.exports = class ReactionRole extends Command {
    constructor (Client) {
        super (Client, 'reactionrole', {
            Aliases : [ 'reactrole', 'rr' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            return new Client.Help(
                Message, {
                    About : 'Create self-assignable roles using reactions on one or multiple messages.',
                    Syntax : 'reactionrole (Command) <Arguments> [Flag]'
                }
            )
        }

        switch (Command) {
            case (Command === 'add' ? Command : '') : {
                try {
                    var MessageID = Arguments[1], ChannelID = Message.channel.id, URL = `https://discord.com/channels/${Message.guild.id}/${Message.channel.id}/${Arguments[1]}`
                    
                    if (isNaN(Arguments[1])) {
                        const IDs = []
                        
                        if (!Arguments[1].startsWith('https://discord.com/channels/') && !Arguments[0].startsWith('https://canary.discord.com/channels/')) {
                            return new Client.Response(
                                Message, `Invalid **Message Link** was provided in your arguments. Try again.`
                            )
                        }

                        for (const ID of String(Arguments[1]).replace('https:', '').replace('discord.com', '').replace('canary.discord.com', '').replace('channels', '').split('/')) { 
                            if (ID.length > 0) IDs.push(ID) 
                        }
                        
                        if (isNaN(IDs[0]) || isNaN(IDs[1]) || isNaN(IDs[2]) || IDs[0] && IDs[1] && !IDs[2] || IDs[0] && !IDs[1] && !IDs[2]) {
                            return new Client.Response(
                                Message, `Invalid format for **Message Link**.`
                            )
                        }

                        MessageID = IDs[2], ChannelID = IDs[1], URL = Arguments[1]
                    }
                    
                    const Channel = Message.guild.channels.cache.get(ChannelID)

                    if (!Channel) { 
                        return new Client.Response(
                            Message, `Couldn't find a **Channel** with that ID.`
                        )
                    }

                    try { 
                        await Channel.messages.fetch(MessageID) 
                    } catch (Error) {
                        return new Client.Response(
                            Message, `Couldn't find a **Message** with that ID.`
                        )
                    }

                    const MessageX = await Channel.messages.fetch(MessageID)
                } catch (Error) {
                    return new Client.Error(
                        Message, 'reactionrole add', Error
                    )
                }
            }
        }
    }
}