const Commands = [ 'add', 'allow', 'authorize', 'remove', 'unauthorize', 'transfer', 'move' ]

const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class Server extends Command {
    constructor (Client) {
        super (
            Client, 'server', {
                Aliases : [ 'guild' ],
                Hidden : true
            }
        )
    }

    async Invoke (Client, Message, Arguments) {
        if (!Client.Staff.includes(Message.author.id)) return
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            return new Client.Help(
                Message, {
                    Syntax : 'server (SubCommand) (Arguments)'
                }
            )
        }

        switch (Command) {
            case (Command === 'add' ? Command : Command === 'allow' ? Command : Command === 'authorize' ? Command : '') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            Syntax : 'server add (Server ID) (Member ID) (Invite Code) [-punish]'
                        }
                    )
                }

                try {
                    const Server = Arguments[1]

                    if (isNaN(Server)) {
                        return new Client.Response(
                            Message, `Couldn't convert **Server** into an integer.`
                        )
                    } 

                    if (!Arguments[2]) {
                        return new Client.Response(
                            Message, `Missing **Member** for authorization.`
                        )
                    }

                    const User = Message.mentions.members.first() || Message.guild.members.cache.get(Arguments[2]) || Message.guild.members.cache.find(m => String(m.user.username).toLowerCase().includes(String(Arguments[2]).toLowerCase()) || String(m.displayName).toLowerCase().includes(String(Arguments[2]).toLowerCase()) || String(m.user.tag).toLowerCase().includes(String(Arguments[2]).toLowerCase())) || Arguments[2]
                    const Member = await Client.users.fetch(Client.users.resolveId(User)).catch(() => {})

                    if (!Member) {
                        return new Client.Response(
                            Message, `Couldn't find a **Member** with the username: **${Arguments[2]}**.`
                        )
                    }

                    Client.Database.query(`SELECT * FROM authorized WHERE server_id = ${Server}`).then(async ([Results]) => {
                        if (Results.length > 0) {
                            return new Client.Response(
                                Message, `Server **${Server}** has already been authorized.`
                            )
                        }

                        Client.Database.query(`INSERT INTO authorized (server_id, member_id, invite_code, punish) VALUES (${Server}, ${Member.id}, 'blair', false)`).catch((Error) => {
                            console.error(Error)
                        })

                        return new Client.Response(
                            Message, `Added **${Server}** as an authorized server.`
                        )
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'server add', Error
                    )
                }

                break
            }

            case (Command === 'remove' ? Command : Command === 'unauthorize' ? Command : '') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            Syntax : 'server remove (Server ID)'
                        }
                    )
                }

                try {
                    const Server = Arguments[1]

                    if (isNaN(Server)) {
                        return new Client.Response(
                            Message, `Couldn't convert **Server** into an integer.`
                        )
                    } 

                    Client.Database.query(`SELECT * FROM authorized`)
                } catch (Error) {
                    return console.error(Error)
                }

                break
            }
        } 
    }
}
