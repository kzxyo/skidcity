const Command = require('../../Structures/Base/command.js')

module.exports = class Prefix extends Command {
    constructor (bot) {
        super (bot, 'prefix', {
            description : 'Show the command prefix',
            commands : [
                {
                    name : 'prefix set',
                    description : 'Set the command prefix',
                    permissions : [ 'Administrator' ],
                    parameters : [ 'prefix' ],
                    syntax : '(prefix)',
                    example : '?'
                }
            ],
            module : 'Servers'
        })

        this.cmds = [
            'set'
        ]
    }

    async execute (bot, message, args, prefix) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !this.cmds.includes(command)) {
            const data = await bot.db.query('SELECT * FROM prefixes WHERE guild_id = $1', {
                bind : [
                    message.guild.id 
                ]
            }).then(([results]) => results)

            const prefix = data.length !== 0 ? data[0].prefix : bot.prefix

            bot.neutral(
                message, `Prefix: \`${prefix}\``
            )
        }

        switch (command) {
            case ('set') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[0], prefix
                        )
                    }

                    const pre = args[1]

                    if (pre.length > 10) {
                        return bot.warn(
                            message, `Prefix must be less than **10 characters**`
                        )
                    }

                    const data = await bot.db.query('SELECT * FROM prefixes WHERE guild_id = $1', {
                        bind : [
                            message.guild.id
                        ]
                    }).then(([results]) => results)

                    if (data.length > 0) {
                        bot.db.query('UPDATE prefixes SET prefix = $1 WHERE guild_id = $2', {
                            bind : [
                                pre, message.guild.id
                            ]
                        })
                    } else {
                        bot.db.query('INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)', {
                            bind : [
                                message.guild.id, pre
                            ]
                        })
                    }

                    bot.approve(
                        message, `Set command **prefix** to \`${pre}\``
                    )

                    bot.prefixes[message.guild.id] = pre
                } catch (error) {
                    return bot.error(
                        message, 'prefix set', error
                    )
                }

                break
            }
        }
    }
}