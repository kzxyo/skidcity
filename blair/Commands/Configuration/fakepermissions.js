const Command = require('../../Structures/Base/Command.js')
const Commands = [ 'add', 'grant', 'remove', 'deny', 'view', 'reset', 'clear' ]

const { EmbedBuilder } = require('discord.js')
const { ActionRowBuilder } = require('discord.js')
const { ButtonBuilder } = require('discord.js')

const Permissions = [
    'Administrator',
    'BanMembers',
    'KickMembers',
    'ManageChannels',
    'ManageEmojisAndStickers',
    'ManageGuild',
    'ManageMessages',
    'ManageNicknames',
    'ManageRoles',
    'ManageWebhooks',
    'ModerateMembers'
]

const PermissionsObject = {
    'administrator' : 'Administrator',
    'banmembers' : 'BanMembers',
    'kickmembers' : 'KickMembers',
    'managechannels' : 'ManageChannels',
    'manageemojisandstickers' : 'ManageEmojisAndStickers',
    'manageguild' : 'ManageGuild',
    'managemessages' : 'ManageMessages',
    'managenicknames' : 'ManageNicknames',
    'manageroles' : 'ManageRoles',
    'managewebhooks' : 'ManageWebhooks',
    'moderatemembers' : 'ModerateMembers'
}

module.exports = class FakePermissions extends Command {
    constructor (Client) {
        super (Client, 'fakepermissions', {
            Aliases : [ 'fakeperms', 'fp' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (Message.author.id !== Message.guild.ownerId) {
            return new Client.Response(
                Message, `Cannot run, **Server Ownership** is a required condition.`
            )
        }

        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !Commands.includes(Command)) {
            return new Client.Help(
                Message, {
                    About : 'Create fake permissions for one or multiple roles in the server.',
                    Syntax : 'fakepermissions (Command) <Arguments>'
                }
            )
        }

        switch (Command) {
            case (Command === 'add' ? Command : Command === 'grant' ? Command : '') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            About : 'Add a fake permission to a role.',
                            Syntax : 'fakepermissions add (Role) (Permission)'
                        }
                    )
                }

                try {
                    const Role = Message.mentions.roles.first() || Message.guild.roles.cache.get(Arguments[1]) || Message.guild.roles.cache.find(Role => String(Role.name).toLowerCase().includes(String(Arguments[1]).toLowerCase()))

                    if (!Role) {
                        return new Client.Response(
                            Message, `Couldn't find a **Role** with that name.`
                        )
                    }

                    if (!Permissions.map((Permission) => String(Permission).toLowerCase()).includes(String(Arguments[2]).toLowerCase())) {
                        return new Client.Response(
                            Message, `Invalid **Permission** was passed. Check permissions at the [Documentation](https://docs.blair.win).`
                        )
                    }

                    const Permission = PermissionsObject[String(Arguments[2]).toLowerCase()]

                    Client.Database.query(`SELECT * FROM fakepermissions WHERE guild_id = $1 AND role_id = $2 AND permission = $3`, {
                        bind : [ Message.guild.id, Role.id, Permission ]
                    }).then(async ([Results]) => {
                        if (Results.length > 0) {
                            return new Client.Response(
                                Message, `Cannot add the same **Fake Permission** twice.`
                            )
                        }

                        Client.Database.query(`INSERT INTO fakepermissions (guild_id, role_id, permission) VALUES ($1, $2, $3)`, {
                            bind : [ Message.guild.id, Role.id, Permission ]
                        })

                        new Client.Response(
                            Message, `Added fake permission **${Permission}** to ${Role}.`
                        )
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'fakepermissions add', Error
                    )
                }

                break
            }

            case (Command === 'remove' ? Command : Command === 'deny' ? Command : '') : {
                if (!Arguments[1]) {
                    return new Client.Help(
                        Message, {
                            About : 'Remove a fake permission from a role.',
                            Syntax : 'fakepermissions remove (Role) (Permission)'
                        }
                    )
                }

                try {
                    const Role = Message.mentions.roles.first() || Message.guild.roles.cache.get(Arguments[1]) || Message.guild.roles.cache.find(Role => String(Role.name).toLowerCase().includes(String(Arguments[1]).toLowerCase()))

                    if (!Role) {
                        return new Client.Response(
                            Message, `Couldn't find a **Role** with that name.`
                        )
                    }

                    if (!Permissions.map((Permission) => String(Permission).toLowerCase()).includes(String(Arguments[2]).toLowerCase())) {
                        return new Client.Response(
                            Message, `Invalid **Permission** was passed. Check permissions at the [Documentation](https://docs.blair.win).`
                        )
                    }

                    const Permission = PermissionsObject[String(Arguments[2]).toLowerCase()]

                    Client.Database.query(`SELECT * FROM fakepermissions WHERE guild_id = $1 AND role_id = $2 AND permission = $3`, {
                        bind : [ Message.guild.id, Role.id, Permission ]
                    }).then(async ([Results]) => {
                        if (Results.length === 0) {
                            return new Client.Response(
                                Message, `Cannot remove a **Fake Permission** that does not exist.`
                            )
                        }

                        Client.Database.query(`DELETE FROM fakepermissions WHERE guild_id = $1 AND role_id = $2 AND permission = $3`, {
                            bind : [ Message.guild.id, Role.id, Permission ]
                        })

                        new Client.Response(
                            Message, `Removed fake permission **${Permission}** from ${Role}.`
                        )
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'fakepermissions remove', Error
                    )
                }

                break
            }

            case (Command === 'view' ? Command : Command === 'list' ? Command : '') : {
                Client.Database.query('SELECT * FROM fakepermissions WHERE guild_id = $1', { bind : [ Message.guild.id ] }).then(async ([Results]) => {
                    if (Results.length === 0) {
                        return new Client.Response(
                            Message, `Couldn't find any **Fake Permissions** for this server.`
                        )
                    }

                    try {
                        const Embeds = [], Pager = Results.Pager(10); var Index = 0

                        for (const Entry of Pager) {
                            const Mapped = Entry.map((Item) => {
                                const Role = Message.guild.roles.cache.get(Item.role_id) 
                                return `\`${++Index}\` ${Role ? Role : 'Unknown Role'} has: **${Item.permission}**` 
                            }).join('\n')
                            
                            Embeds.push(new EmbedBuilder({
                                title : 'Fake Permissions',
                                description : Mapped,
                                footer : {
                                    text : `Page 1/1 (${Index} ${Index === 1 ? 'entry' : 'entries'})`
                                }
                            }).setColor(Client.Color))
                        }

                        if (Embeds.length > 1) { 
                            const Paginator = new Client.Paginator(Message)
                            
                            Paginator.SetEmbeds(Embeds)
                            
                            await Paginator.Send() 
                        } else { 
                            return Message.channel.send({ 
                                embeds: [
                                    Embeds[0]
                                ] 
                            }) 
                        }
                    } catch (Error) {
                        return new Client.Error(
                            Message, 'fakepermissions view', Error
                        )
                    }
                })

                break
            }

            case (Command === 'reset' ? Command : Command === 'clear' ? Command : '') : {
                try {
                    const Confirm = await Message.channel.send({
                        embeds : [
                            new EmbedBuilder({
                                title : 'Confirm',
                                description : 'Would you like to remove every **Fake Permission**?'
                            }).setColor(Client.Color)
                        ],
                        components : [
                            new ActionRowBuilder().addComponents(
                                new ButtonBuilder({
                                    label : 'Approve',
                                    customId : 'Approve',
                                }).setStyle('Primary'),
                                new ButtonBuilder({
                                    label : 'Decline',
                                    customId : 'Decline'
                                }).setStyle('Secondary')
                            )
                        ]
                    })

                    const Collector = Confirm.createMessageComponentCollector({ time : 100000 })

                    Collector.on('collect', async (Interaction) => {
                        await Interaction.deferUpdate()

                        if (Interaction.user.id !== Message.author.id) {
                            return
                        }

                        switch (Interaction.customId) {
                            case ('Approve') : {
                                Confirm.delete()

                                Client.Database.query(`DELETE FROM fakepermissions WHERE guild_id = $1`, {
                                    bind : [ Message.guild.id ]
                                }).then(() => {
                                    return new Client.Response(
                                        Message, `Removed every **Fake Permission** from this server.`
                                    )
                                })

                                Collector.stop()

                                break
                            }

                            case ('Decline') : {
                                Confirm.delete()
                                Message.delete()
                                Collector.stop()

                                break
                            }
                        }
                    })
                } catch (Error) {
                    return new Client.Error(
                        Message, 'fakepermissions reset', Error
                    )
                }

                break
            }
        }
    }
}