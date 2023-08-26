const Base = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const commands = [
    'enable', 'unlock',
    'disable', 'lock',
    'restrict', 'permit'
]

module.exports = class Command extends Base {
    constructor (bot) {
        super (bot, 'command', {
            description : 'Manage the accessibility of commands',
            permissions : [ 'ManageChannels' ],
            syntax : '(subcommand) <args>',
            example : 'disable #chat ping',
            aliases : [ 'cmd' ],
            commands : [
                {
                    name : 'command enable',
                    description : 'Enable a command which was previously disabled',
                    permissions : [ 'ManageChannels' ],
                    syntax : '(channel) (command)',
                    example : '#chat ping',
                    aliases : [ 'unlock' ]
                },
                {
                    name : 'command disable',
                    description : 'Disable a command within a channel',
                    permissions : [ 'ManageChannels' ],
                    syntax : '(channel) (command)',
                    example : '#chat ping',
                    aliases : [ 'lock' ],
                    commands : [
                        {
                            name : 'command disable list',
                            description : 'View all disabled commands',
                            permissions : [ 'ManageChannels' ],
                            aliases : [ 'ls' ]
                        }
                    ]
                },
                {
                    name : 'command restrict',
                    description : 'Restrict command access to roles',
                    permissions : [ 'ManageGuild' ],
                    syntax : '(role) (command)',
                    example : '@Friends ping',
                    aliases : [ 'permit' ],
                    commands : [
                        {
                            name : 'command restrict list',
                            description : 'View all restricted commands',
                            permissions : [ 'ManageGuild' ],
                            aliases : [ 'ls' ]
                        }
                    ]
                }
            ],
            module : 'Servers'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !commands.includes(command)) {
            return message.help()
        }

        switch (true) {
            case (command === 'enable' || command === 'unlock') : {
                try {
                    if (!args[1]) { 
                        return message.help()
                    }

                    if (args[1].toLowerCase() === 'all') {
                        const command = await bot.converters.command(message, args.slice(2).join(' '), { response : true })

                        if (!command) {
                            return
                        }

                        const IDs = message.guild.channels.cache.filter((channel) => channel.type === 0).map((channel) => channel.id)

                        const data = await bot.db.query('SELECT channel_id FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = ANY ($3)', {
                            bind : [
                                message.guild.id, command.name, IDs
                            ]
                        }).then(([results]) => results.map((result) => result.channel_id))

                        const state = await Promise.all(
                            IDs.map((ID) => {
                                if (data.includes(ID)) {
                                    bot.db.query('DELETE FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = $3', {
                                        bind : [
                                            message.guild.id, command.name, ID
                                        ]
                                    })

                                    return true
                                } else {
                                    return false
                                }
                            })
                        )

                        const enabled = state.filter((I) => I === true).length

                        if (enabled === 0) {
                            return message.warn(`Command \`${command.name}\` is already enabled in every channel`)
                        }

                        message.approve(`Enabled command \`${command.name}\` in **${enabled}** ${enabled === 1 ? 'channel' : 'channels'}`)
                    } else {
                        const channel = await bot.converters.channel(message, args[1], { response : true })

                        if (!channel) {
                            return
                        }

                        const command = await bot.converters.command(message, args.slice(2).join(' ').toLowerCase(), { response : true })

                        if (!command) {
                            return
                        }

                        const data = await bot.db.query('SELECT * FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = $3', {
                            bind : [
                                message.guild.id, command.name, channel.id
                            ]
                        }).then(([results]) => results[0])

                        if (!data) {
                            return message.warn(`Command \`${command.name}\` is already enabled in ${channel}`)
                        }

                        bot.db.query('DELETE FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = $3', {
                            bind : [
                                message.guild.id, command.name, channel.id
                            ]
                        })

                        message.approve(`Enabled command \`${command.name}\` in ${channel}`)
                    }
                } catch (error) {
                    return message.error(error)
                }

                break
            }
            
            case (command === 'disable' || command === 'lock') : {
                if (!args[1]) {
                    return message.help()
                }

                const arg = args[1].toLowerCase()

                if (arg === 'list' || arg === 'ls') {
                    try {
                        const data = await bot.db.query('SELECT * FROM commands.disabled WHERE guild_id = $1', {
                            bind : [
                                message.guild.id
                            ]
                        }).then(([results]) => results)

                        if (!data.length) {
                            return message.warn(`There aren't any **disabled commands** in this server`)
                        }

                        let index = 0

                        const pages = data.list(10)
                        
                        const embeds = await Promise.all(
                            pages.map((page) => {
                                const entries = page.map((I) => {
                                    const channel = bot.channels.cache.get(I.channel_id) 
                                    
                                    return `\`${++index}\` **${I.command}** in ${channel}`
                                }).join('\n')
                                
                                return new Discord.EmbedBuilder({
                                    author : {
                                        name : message.member.displayName,
                                        iconURL : message.member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    },
                                    title : 'Disabled Commands',
                                    description : entries
                                }).setColor(bot.colors.neutral)
                            })
                        )

                        await new bot.paginator(
                            message, {
                                embeds : embeds,
                                entries : index,
                            }
                        ).construct()
                    } catch (error) {
                        return message.error()
                    }
                } else {
                    try {
                        if (arg === 'all') {
                            const command = await bot.converters.command(message, args.slice(2).join(' '), { response : true })
    
                            if (!command) {
                                return
                            }
    
                            const IDs = message.guild.channels.cache.filter((channel) => channel.type === 0).map((channel) => channel.id)
    
                            const data = await bot.db.query('SELECT channel_id FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = ANY ($3)', {
                                bind : [
                                    message.guild.id, command.name, IDs
                                ]
                            }).then(([results]) => results.map((result) => result.channel_id))
    
                            const state = await Promise.all(
                                IDs.map((ID) => {
                                    if (!data.includes(ID)) {
                                        bot.db.query('INSERT INTO commands.disabled (guild_id, command, channel_id) VALUES ($1, $2, $3)', {
                                            bind : [
                                                message.guild.id, command.name, ID
                                            ]
                                        })
    
                                        return true
                                    } else {
                                        return false
                                    }
                                })
                            )
    
                            const disabled = state.filter((I) => I === true).length
    
                            if (disabled === 0) {
                                return message.warn(`Command \`${command.name}\` is already disabled in every channel`)
                            }
    
                            message.approve(`Disabled command \`${command.name}\` in **${disabled}** ${disabled === 1 ? 'channel' : 'channels'}`)
                        } else {
                            const channel = await bot.converters.channel(message, args[1], { response : true })
    
                            if (!channel) {
                                return
                            }
    
                            const command = await bot.converters.command(message, args.slice(2).join(' ').toLowerCase(), { response : true })
    
                            if (!command) {
                                return
                            }
    
                            const data = await bot.db.query('SELECT * FROM commands.disabled WHERE guild_id = $1 AND command = $2 AND channel_id = $3', {
                                bind : [
                                    message.guild.id, command.name, channel.id
                                ]
                            }).then(([results]) => results[0])
    
                            if (data) {
                                return message.warn(`Command \`${command.name}\` is already disabled in ${channel}`)
                            }
    
                            bot.db.query('INSERT INTO commands.disabled (guild_id, command, channel_id) VALUES ($1, $2, $3)', {
                                bind : [
                                    message.guild.id, command.name, channel.id
                                ]
                            })
    
                            message.approve(`Disabled command \`${command.name}\` in ${channel}`)
                        } 
                    } catch (error) {
                        return message.error(error)
                    }
                }
            }
            case (command === 'restrict' || command === 'permit') : {}
        }
    }
}