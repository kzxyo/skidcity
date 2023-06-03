const Command = require('../../Structures/Base/Command.js')
const Commands = [ 'set', 'reset' ]

module.exports = class Prefix extends Command {
    constructor (Client) {
        super (Client, 'prefix', {

        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            Client.Database.query(`SELECT * FROM prefixes WHERE guild_id = $1`, { bind : [Message.guild.id] }).then(async ([Results]) => {
                return new Client.Response(
                    Message, `Server Prefix: \`${Results.length > 0 ? Results[0].prefix : Client.DefaultPrefix}\``
                )
            })
        }
 
        switch (Command) {
            case ('set') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            About : 'Set a new server prefix for commands.',
                            Syntax : 'prefix set (New Prefix)'
                        }
                    )
                }

                try {
                    if (!Message.member.permissions.has('Administrator')) {
                        return new Client.Response(
                            Message, `Permission \`Administrator\` is required to change server prefix.`
                        )
                    }

                    if (Arguments[1].length >= 10) {
                        return new Client.Response(
                            Message, `You cannot set a **Server Prefix** with more than **10** characters.`
                        )
                    }

                    Client.Database.query(`SELECT * FROM prefixes WHERE guild_id = $1`, { bind : [Message.guild.id] }).then(async ([Results]) => {
                        if (Results.length === 0) {
                            Client.Database.query(`INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)`, {
                                bind : [ Message.guild.id, Arguments[1] ]
                            }) 
                        } else {
                            Client.Database.query(`UPDATE prefixes SET prefix = $1 WHERE guild_id = $2`, { 
                                bind : [Arguments[1], Message.guild.id] 
                            })
                        }

                        new Client.Response(
                            Message, `Your **Server Prefix** has been set as \`${Arguments[1]}\``
                        )
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'prefix set', Error
                    )
                }

                break
            }

            case ('reset') : {
                try {
                    if (!Message.member.permissions.has('Administrator')) {
                        return new Client.Response(
                            Message, `Permission \`Administrator\` is required to change server prefix.`
                        )
                    }

                    Client.Database.query(`DELETE FROM prefixes WHERE guild_id = $1`, { 
                        bind : [Message.guild.id] 
                    })

                    new Client.Response(
                        Message, `Reset **Server Prefix** back to default.`
                    )
                } catch (Error) {
                    return new Client.Error(
                        Message, 'prefix reset', Error
                    )
                }

                break
            }
        }
    }
}