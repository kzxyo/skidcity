const Commands = [ 'rename' ]

const Command = require('../../Structures/Base/Command.js')

module.exports = class Role extends Command {
    constructor (Client) {
        super (Client, 'role', {
            Aliases : [ 'r' ],

            Permissions : [ 'ManageRoles' ]
        })
    }
    
    async Invoke (Client, Message, Arguments) {
        if (!Arguments[0]) {
            return new Client.Help(
                Message, {
                    Description : 'Manage & Modify roles within the server.',
                    Usage : 'role (Member) (Role)'
                }
            )
        }

        if (Commands.includes(Command)) {
            switch (Command) {
                case ('rename') : {

                }
            }
        } else {
            try {
                const Member =  Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(Member => Member.displayName.toLowerCase().includes(Arguments[0].toLowerCase()) || Member.user.username.toLowerCase().includes(Arguments[0].toLowerCase()) || Member.user.tag.toLowerCase().includes(Arguments[0].toLowerCase())) || Message.mentions.members.last()

                if (!Member) {
                    return new Client.Response(
                        Message, `Couldn't find a member with the username: **${Arguments[0]}**.`
                    )
                }

                if (!Arguments[1]) {
                    return new Client.Response(
                        Message, `Missing a **Role** to **Add**/**Remove** **To**/**From** a member.`
                    )
                }

                if (Arguments.slice(1).join(' ').split(',').length === 1 || Arguments.slice(1).join(' ').endsWith(',')) {
                    const Role = Message.mentions.roles.first() || Message.guild.roles.cache.get(Arguments[1]) || Message.guild.roles.cache.find(Role => Role.name.toLowerCase().includes(Arguments.slice(1).join(' ').toLowerCase()))

                    if (!Role) {
                        return new Client.Response(
                            Message, `Couldn't find a **Role** with the name: **${Arguments.slice(1).join(' ')}**.`
                        )
                    }

                    if (Message.author.id !== Message.guild.ownerId && Message.member.roles.highest.position <= Role.position) {
                        return new Client.Response(
                            Message, `Cannot perform **Action**: ${Role} is too high for you to manage.`
                        )
                    }

                    if (Member.roles.cache.get(Role.id)) {
                        await Member.roles.remove(Role.id)

                        return new Client.Response(
                            Message, `Removed **${Role.name}** from member **${Member.user.tag}**.`
                        )
                    } else if (!Member.roles.cache.get(Role.id)) {
                        await Member.roles.add(Role.id)

                        return new Client.Response(
                            Message, `Added **${Role.name}** to member **${Member.user.tag}**.`
                        )
                    }
                } else {
                    const Roles = [], FailedRoles = []

                    for (var String of Arguments.slice(1).join(' ').split(',')) {
                        String = String.toString().trim().startsWith('<@&') ? String.replace('<@&', '').replace('>', '').toString().trim() : String.toString().trim() 
                        
                        const Role = Message.guild.roles.cache.get(String) || Message.guild.roles.cache.find((Role) => Role.name.toLowerCase().includes(String.toLowerCase()))

                        if (Role) {
                            if (Message.author.id !== Message.guild.ownerId && Message.member.roles.highest.position <= Role.position) { 
                                FailedRoles.push({
                                    Role : Role.id,
                                    Check : Member.roles.cache.get(Role.id) ? 'remove' : 'add' 
                                })
                            } else { 
                                Roles.push({ 
                                    Role : Role.id, 
                                    Check : Member.roles.cache.get(Role.id) ? 'remove' : 'add' 
                                }) 
                            }
                        }
                    }

                    if (FailedRoles.length >= 1) {
                        return new Client.Response(
                            Message, `Couldn't ${FailedRoles[0].Check === 'add' ? 'add' : 'remove'} **${Message.guild.roles.cache.get(FailedRoles[0].Role).name}** ${FailedRoles[0].Check === 'add' ? 'to' : 'from'} member **${Member.user.tag}**.`
                        )
                    } else {
                        const ChangedRoles = []

                        for (const Role of Roles) {
                            if (Role.Check === 'add') {
                                ChangedRoles.push(`+${Message.guild.roles.cache.get(Role.Role).name}`)
    
                                await Member.roles.add(Role.Role)
                            } else if (Role.Check === 'remove') {
                                ChangedRoles.push(`-${Message.guild.roles.cache.get(Role.Role).name}`)
    
                                await Member.roles.remove(Role.Role)
                            }
                        }

                        return new Client.Response(
                            Message, `Changed Roles for **${Member.user.tag}**: *${ChangedRoles.join(', ')}*.`
                        )
                    }
                }
            } catch (Error) {
                return new Client.Error(
                    Message, 'role', Error
                )
            }
        }
    }
}