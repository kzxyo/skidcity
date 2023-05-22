const Command = require('../../Structures/Base/Command.js')

module.exports = class Ban extends Command {
    constructor (Client) {
        super (Client, 'ban', {
            Aliases : [ 'b' ],

            Permissions : ['BanMembers']
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (!Arguments[0]) {
            return Message.channel.send('who i smoke')
        }

        const User = Message.mentions.members.first() || Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(m => String(m.user.username).toLowerCase().includes(String(Arguments[0]).toLowerCase()) || String(m.displayName).toLowerCase().includes(String(Arguments[0]).toLowerCase()) || String(m.user.tag).toLowerCase().includes(String(Arguments[0]).toLowerCase())) || Arguments[0]

        try {
            const Resolved = await Client.users.fetch(Client.users.resolveId(User)).catch(() => {})

            if (Resolved.id === Client.user.id) {
                return await Message.channel.send('why u tryna smoke me')
            }

            if (Resolved.id === Message.author.id) {
                return await new Client.Response(
                    Message, `You cannot **Ban** yourself.`
                )
            }

            if (Resolved.id === Message.guild.ownerId) {
                return await new Client.Response(
                    Message, `You cannot **Ban** the owner of the server.`
                )
            }

            if (Message.author.id !== Message.guild.ownerId) {
                if (Message.guild.members.cache.get(Resolved.id) && Message.member.roles.highest.position === Message.guild.members.cache.get(Resolved.id).roles.highest.position) {
                    return await new Client.Response(
                        Message, `You cannot **Ban** a member with the same top role as you.`
                    )
                }
    
                if (Message.guild.members.cache.get(Resolved.id) && Message.member.roles.highest.position < Message.guild.members.cache.get(Resolved.id).roles.highest.position) {
                    return await new Client.Response(
                        Message, `You cannot **Ban** a member with a higher role than you.`
                    )
                }
            }

            if (Message.guild.members.cache.get(Resolved.id) && Message.guild.members.cache.get(Client.user.id).roles.highest.position <= Message.guild.members.cache.get(Resolved.id).roles.highest.position) {
                return await new Client.Response(
                    Message, `Couldn't perform action on that **Member**: Insufficient permissions.`
                )
            }

            const DeleteDays = isNaN(Arguments[1]) ? 0 : parseInt(Arguments[1])
            const Reason = Arguments.slice(DeleteDays === 0 ? 1 : 2).join(' ') || 'No reason was provided for this action.'

            Message.guild.members.ban(Resolved.id, {
                days : DeleteDays > 7 ? 7 : DeleteDays,
                reason : `Member Responsible: ${Message.author.tag} / ${Reason}`
            })

            Message.channel.send(`Banned **${Resolved.tag}** from the server.`)

            return new Client.Case(Client, Message).Insert(
                Message.author, Resolved, 'Banned', Reason, 'None', 'None'
            )
        } catch (Error) {
            return console.log(Error)
            // Do This Later. 
        }
    }
}