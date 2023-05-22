const Command = require('../../Structures/Base/Command.js')

module.exports = class Welcome extends Command {
    constructor (Client) {
        super (Client, 'welcome', {
            Permissions : [ 'ManageGuild' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] && !['add'].includes(Command)) {
            return new Client.Help(
                Message, {

                }
            )
        }

        switch (Command) {
            case ('add') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {

                        }
                    )
                }
                
                try {
                    const Channel = Message.mentions.channels.first() || Message.guild.channels.cache.get(Arguments[1]) || Message.guild.channels.cache.find((Channel) => Channel.name.includes(String(Arguments[1]).toLowerCase()))

                    if (!Channel) {
                        return new Client.Response(
                            Message, `Couldn't find a **Channel** with that name.`
                        )
                    }

                    if (!Arguments[2] || Arguments[2].startsWith('--')) {
                        return new Client.Response(
                            Message, `Missing a **Response** to output in a channel.`
                        )
                    }

                    var SelfDestruct = false, DeleteOnLeave = false
                    for (const String of Arguments.slice(2).join(' ').split('--').values()) {
                        switch (String) {
                            case (String.startsWith('self_destruct') ? String : '') : {
                                SelfDestruct = String.replace('self_destruct', '').trim()

                                break
                            }
                            
                            case ('delete_on_leave') : {
                                DeleteOnLeave = true

                                break
                            }
                        }
                    }

                    const Response = Arguments.slice(2).join(' ').split('--')[0]

                    Client.Database.query('SELECT * FROM welcomes WHERE guild_id = $1 AND channel_id = $2', {
                        bind : [ Message.guild.id, Channel.id ]
                    }).then(async ([Results]) => {
                        if (Results.length > 0) {
                            return new Client.Response(
                                Message, `Cannot create multiple **Join Messages** for one channel.`
                            )
                        }

                        Client.Database.query('INSERT INTO welcomes (guild_id, channel_id, response, self_destruct, delete_on_leave) VALUES ($1, $2, $3, $4, $5)', {
                            bind : [ Message.guild.id, Channel.id, Response, SelfDestruct === false ? null : String(parseInt(SelfDestruct) * 1000), DeleteOnLeave ]
                        }).then(() => {
                            return new Client.Response(
                                Message, `Added a **Join Message** for ${Channel} with ${Response.startsWith('{embed}') ? 'an embed response' : 'a text response'}.\n${SelfDestruct ? `Join Messages are set to self destruct after \`${SelfDestruct}\` seconds.` : ''}`
                            )
                        })
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'welcome add', Error
                    )
                }

                break
            }
        }
    }
}