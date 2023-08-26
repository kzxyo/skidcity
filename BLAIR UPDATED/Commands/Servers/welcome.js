const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

module.exports = class Welcome extends Command {
    constructor (bot) {
        super (bot, 'welcome', {
            description : 'Set up welcome messages',
            permissions : [ 'ManageGuild' ],
            syntax : '(command) <arguments>',
            example : 'add #message Hi {user.mention}!',
            aliases : [ 'welc' ],
            commands : [
                {
                    name : 'welcome add',
                    description : 'Add a welcome message to a channel',
                    permissions : [ 'ManageGuild' ],
                    parameters : [ 'channel', 'message' ],
                    syntax : '(channel) (message)',
                    example : '#message Hi {user.mention}!',
                    aliases : [ 'create' ],
                    flags : [
                        {
                            name : 'self_destruct',
                            description : 'The amount of time (in seconds) before deleting the message',
                            aliases : [ 'sd', 'destruct', 'd' ],
                            converter : Number,
                            maximum : 120,
                            minimum : 5
                        }
                    ]
                },
                {
                    name : 'welcome list',
                    description : 'Show all welcome messages',
                    permissions : [ 'ManageGuild' ],
                    aliases : [ 'show' ]
                },
                {
                    name : 'welcome remove',
                    description : 'Remove a welcome message from a channel',
                    permissions : [ 'ManageGuild' ],
                    parameters : [ 'channel' ],
                    syntax : '(channel)',
                    example : '#message',
                    aliases : [ 'rm', 'delete', 'del' ]
                },
                {
                    name : 'welcome reset',
                    description : 'Remove all welcome messages',
                    permissions : [ 'ManageGuild' ],
                    aliases : [ 'clear' ]
                },
                {
                    name : 'welcome view',
                    description : 'Show the welcome message for a channel',
                    permissions : [ 'ManageGuild' ],
                    parameters : [ 'channel' ],
                    syntax : '<channel>',
                    example : '#message',
                    aliases : [ 'view', 'check', 'test', 'emit' ]
                }
            ],
            module : 'Servers'
        })

        this.cmds = [
            'add', 'create',
            'list', 'show',
            'remove', 'rm', 'delete', 'del',
            'reset', 'clear',
            'view', 'check', 'test', 'emit'
        ]
    }

    async execute (bot, message, args, prefix) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !this.cmds.includes(command)) {
            return bot.help(
                message, this, prefix
            )
        }

        switch (command) {
            case (command === 'add' ? command : command === 'create' ? command : '') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[0], prefix
                        )
                    }

                    const channel = await bot.converters.channel(
                        message, args[1], {
                            response : true,
                            type : 0
                        }
                    )

                    if (!channel) {
                        return
                    }

                    if (!args[2]) {
                        return bot.warn(
                            message, 'Missing a **message** to output'
                        )
                    }

                    const msg = await bot.variables.convert(
                        args.slice(2).join(' '), {
                            message : message
                        }
                    )

                    const welcome = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1 AND channel_id = $2', {
                        bind : [
                            message.guild.id, channel.id 
                        ]
                    }).then(([results]) => results[0])

                    if (welcome) {
                        return bot.warn(
                            message, `Already sending a **welcome message** to ${channel}`
                        )
                    }

                    const self_destruct = message.parameters['self_destruct']

                    if (self_destruct?.success === false) {
                        return bot.warn(
                            message, self_destruct.message
                        )
                    }

                    const self_destruct_value = self_destruct?.value ?? null

                    await bot.db.query('INSERT INTO system.welcomes (guild_id, channel_id, message, self_destruct) VALUES ($1, $2, $3, $4)', {
                        bind : [ 
                            message.guild.id, channel.id, msg, self_destruct_value
                        ]
                    })

                    const code = new bot.MessageParser(bot, msg)

                    bot.approve(
                        message, `Created ${code.embeds.length ? 'an embed' : ' a text'} **welcome message** for ${channel}`, {
                            text : self_destruct_value ? `**Self-destruct** has been set for \`${self_destruct_value}\` seconds` : null
                        }
                    )
                } catch (error) {
                    return bot.error(
                        message, 'welcome add', error
                    )
                }

                break
            }

            case (command === 'list' ? command : command === 'show' ? command : '') : {
                try {
                    const welcomes = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1', {
                        bind : [
                            message.guild.id
                        ]
                    }).then(([results]) => results)

                    if (!welcomes.length) {
                        return bot.warn(
                            message, `No **welcome messages** found`
                        )
                    }

                    let index = 0

                    const pages = welcomes.list(10), embeds = await Promise.all(
                        pages.map((page) => {
                            const entries = page.map((I) => {
                                const channel = message.guild.channels.cache.get(I.channel_id)
                                
                                return `\`${++index}\` ${channel ? channel : 'Deleted Channel'}`
                            }).join('\n')
                            
                            return new Discord.EmbedBuilder({
                                author : {
                                    name : message.member.displayName,
                                    iconURL : message.member.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                title : 'Welcome Channels',
                                description : entries
                            }).setColor(bot.colors.neutral)
                        })
                    )

                    await new bot.paginator(
                        message, {
                            embeds : embeds,
                            entries : index,
                            text : `Page {page} of {pages} ({entries} entries)`
                        }
                    ).construct()
                } catch (error) {
                    return bot.error(
                        message, 'welcome list', error
                    )
                }

                break
            }

            case (command === 'remove' ? command : command === 'rm' ? command : command === 'delete' ? command : command === 'del' ? command : '') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[2]
                        )
                    }

                    const welcomes = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1', {
                        bind : [
                            message.guild.id
                        ]
                    }).then(([results]) => results)

                    const entry = bot.util.entry(welcomes, args[1])

                    if (entry) {
                        await bot.db.query('DELETE FROM system.welcomes WHERE guild_id = $1 AND channel_id = $2', {
                            bind : [
                                message.guild.id, entry.channel_id
                            ]
                        })

                        const channel = message.guild.channels.cache.get(entry.channel_id)
                        
                        bot.approve(
                            message, `Removed the **welcome message** from ${channel ? channel : 'Deleted Channel'}`
                        )
                    } else {
                        const channel = await bot.converters.channel(
                            message, args[1], {
                                response : true,
                                type : 0
                            }
                        )
    
                        if (!channel) {
                            return
                        }

                        const welcome = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1 AND channel_id = $2', {
                            bind : [
                                message.guild.id, channel.id 
                            ]
                        }).then(([results]) => results[0])

                        if (!welcome) {
                            return bot.warn(
                                message, `No **welcome message** found for ${channel}`
                            )
                        }

                        await bot.db.query('DELETE FROM system.welcomes WHERE guild_id = $1 AND channel_id = $2', {
                            bind : [
                                message.guild.id, channel.id
                            ]
                        })

                        bot.approve(
                            message, `Removed the **welcome message** from ${channel}`
                        )
                    }
                } catch (error) {
                    return bot.error(
                        message, 'welcome remove', error
                    )
                }

                break
            }

            case (command === 'reset' ? command : command === 'clear' ? command : '') : {
                try {
                    const welcomes = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1', {
                        bind : [
                            message.guild.id
                        ]
                    }).then(([results]) => results[0])

                    if (!welcomes) {
                        return bot.warn(
                            message, `No **welcome messages** found`
                        )
                    }

                    await bot.confirm(
                        message, `Are you sure that you would like to remove all **welcome messages**?`, async () => {
                            await bot.db.query('DELETE FROM system.welcomes WHERE guild_id = $1', {
                                bind : [
                                    message.guild.id
                                ]
                            })

                            bot.approve(
                                message, `Removed all **welcome messages**`
                            )
                        }
                    )
                } catch (error) {
                    return bot.error(
                        message, 'welcome reset', error
                    )
                }

                break
            }

            case (command === 'view' ? command : command === 'check' ? command : command === 'test' ? command : command === 'emit' ? command : '') : {
                try {
                    const channel = args[1] ? await bot.converters.channel(
                        message, args[1], {
                            response : true,
                            type : 0
                        } 
                    ) : message.channel

                    if (!channel) {
                        return
                    }

                    const welcome = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1 AND channel_id = $2', {
                        bind : [
                            message.guild.id, channel.id 
                        ]
                    }).then(([results]) => results[0])

                    if (!welcome) {
                        return bot.warn(
                            message, `No **welcome message** found for ${channel}`
                        )
                    }

                    const msg = new bot.MessageParser(
                        bot, await bot.variables.convert(
                            welcome.message, {
                                user : message.author,
                                member : message.member,
                                guild : message.guild,
                                channel : message.channel
                            }   
                        )
                    )

                    message.channel.send(msg)
                } catch (error) {
                    return bot.error(
                        message, 'welcome view', error
                    )
                }

                break
            }
        }
    }
}