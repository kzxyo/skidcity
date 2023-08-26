const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

module.exports = class Help extends Command {
    constructor (bot) {
        super (bot, 'help', {
            description : 'Show information about a command',
            parameters : [ 'command' ],
            syntax : '<command>',
            example : 'ping',
            aliases : [ 'h' ],
            module : 'Information'
        })
    }

    async execute (bot, message, args) {
        try {
            if (!args[0]) {
                const modules = [ 'Music', 'Servers', 'Moderation', 'Information', 'Miscellaneous', 'Last.fm Integration' ]

                const embeds = await Promise.all(
                    modules.map((module) => {
                        const entries = bot.commands.filter((command) => command.module === module).map((command) => {
                            const subCommands = bot.subCommands.filter((subCommand) => subCommand.name.startsWith(command.name)).map((subCommand) => subCommand)

                            if (subCommands.length) {
                                const entries = [ command, ...subCommands ].map((I) => {
                                    return `[\`${I.name}\`](https://discord.gg/blair)`
                                })
                                
                                return entries.join('\n> ')
                            } else {
                                return `[\`${command.name}\`](https://discord.gg/blair)`
                            }
                        })

                        const total = entries.reduce((total, entry) => {
                            const number = (entry.match(/[\n]/g) || []).length

                            return total + number
                        }, 0) + entries.length

                        return new Discord.EmbedBuilder({
                            description : `\`\`\`ini\n[ ${module} ]\n[ ${total} ${total === 1 ? 'command' : 'commands'} ]\`\`\`\n> ${entries.map((command) => command).join('\n> ')}`,
                            thumbnail : {
                                url : bot.user.displayAvatarURL()
                            }
                        }).setColor(bot.colors.neutral)
                    })
                )

                embeds.unshift(
                    new Discord.EmbedBuilder({
                        description : `\`\`\`ini\n[ ${bot.commands.size + bot.subCommands.size} commands ]\`\`\`\n> ${modules.map((module) => `[\`${module}\`](https://discord.gg/blair)`).join('\n> ')}`,
                        thumbnail : {
                            url : bot.user.displayAvatarURL()
                        }
                    }).setColor(bot.colors.neutral)
                )

                await new bot.paginator(
                    message, {
                        embeds : embeds
                    }
                ).construct()
            } else {
                const command = await bot.converters.command(
                    message, args.join(' '), {
                        response : true
                    }
                )

                if (!command) {
                    return
                }

                const help = new Discord.EmbedBuilder({
                    author : {
                        name : command.module,
                        iconURL : bot.user.displayAvatarURL()
                    },
                    description : `${command.description || ''}\n>>> \`\`\`bf\nSyntax: ${message.prefix}${command.syntax ? `${command.name} ${command.syntax}` : command.name}\n${command.example ? `Example: ${message.prefix}${command.name} ${command.example}` : ''}\`\`\``,
                    fields : [
                        {
                            name : 'Aliases',
                            value : `\`${command.aliases ? command.aliases.join('`, `') : 'N/A'}\``,
                            inline : true
                        },
                        {
                            name : 'Parameters',
                            value : `\`${command.parameters ? command.parameters.join('\`, \`') : 'N/A'}\``,
                            inline : true
                        },
                        {
                            name : 'Permissions',
                            value : `\`${command.permissions ? command.permissions.join('\`, \`').replace(/[A-Z]/g, (match) => ` ${match}`).replace('And', '&').trim() : 'N/A'}\``,
                            inline : true
                        }
                    ]
                }).setColor(bot.colors.neutral)

                if (command.flags) {
                    help.addFields(
                        {
                            name : 'Optional Parameters',
                            value : command.flags.map((flag) => {
                                const arg = flag.converter ? ` ${flag.converter === String && flag.multiple ? `\`str\`` : flag.converter === Number && flag.minimum && flag.maximum ? `(\`${flag.minimum}\` - \`${flag.maximum}\`)` : ''}` : ''
                                return `\`${flag.converter ? '--' : '-'}${flag.name}\`${arg}${flag.description ? `\n> ${flag.description}` : ''}`
                            }).join('\n')
                        }
                    )
                }

                let embeds = []

                if (command.commands) {
                    const pages = bot.subCommands.filter((subCommand) => subCommand.name.startsWith(command.name)).map((subCommand) => subCommand).list(15)

                    embeds = await Promise.all(
                        pages.map((page) => {
                            const entries = page.map((I) => {
                                return `> \`${I.name}\` - ${I.description ? `${I.description.slice(0, 33).trim()}${I.description.length > 33 ? '..' : ''}` : 'N/A'}`
                            }).join('\n')

                            return new Discord.EmbedBuilder(help).addFields(
                                {
                                    name : 'Subcommands',
                                    value : entries
                                }
                            )
                        })
                    )
                } else {
                    embeds = [ help ]
                }

                await new bot.paginator(
                    message, {
                        embeds : embeds
                    }
                ).construct()
            }
        } catch (error) {
            return bot.error(
                message, 'help', error
            )
        }
    }
}