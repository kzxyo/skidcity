const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const commands = [
    'add',
    'list', 'ls',
    'remove', 'rm'
]

module.exports = class Whitelist extends Command {
    constructor (bot) {
        super (bot, 'whitelist', {
            description : 'Manage server whitelists',
            syntax : '(subcommand) <arguments>',
            example : `add ${bot.owner.username} 102998626..`,
            aliases : [ 'wl' ],
            commands : [
                {
                    name : 'whitelist add',
                    description : 'Add a server to the whitelist',
                    parameters : [ 'user', 'guild' ],
                    syntax : '(user) (guild id)',
                    example : `${bot.owner.username} 102998626..`
                },
                {
                    name : 'whitelist list',
                    description : 'View all whitelisted servers for a user',
                    parameters : [ 'user' ],
                    syntax : '(user)',
                    example : `${bot.owner.username}`,
                    aliases : [ 'ls' ]
                },
                {
                    name : 'whitelist remove',
                    description : 'Remove a server from the whitelist',
                    parameters : [ 'guild' ],
                    syntax : '(guild id)',
                    example : '1029986260393136168',
                    aliases : [ 'rm' ]
                }
            ],
            module : 'Developer',
            guarded : true
        })
    }

    async execute (bot, message, args) {
        if (![ '944099356678717500', '671744161107410968' ].includes(message.author.id)) return

        const command = String(args[0]).toLowerCase()

        if (!args[0] || !commands.includes(command)) {
            return bot.help(
                message, this
            )
        }

        switch (true) {
            case (command === 'add' || command === 'create') : {
                try {
                    if (!args[1] || !args[2]) {
                        return bot.help(
                            message, this.commands[0]
                        )
                    }

                    const member = await bot.converters.member(
                        message, args[1], {
                            response : true
                        }
                    )

                    if (!member) {
                        return
                    }

                    const ID = args[2]

                    if (isNaN(ID) || ID.length < 17 || ID.length > 20) {
                        return bot.warn(
                            message, `Invalid **server ID**`
                        )
                    }

                    const URL = bot.OAuth2({
                        scopes : [
                            'bot'
                        ],
                        guildId : ID,
                        disableGuildSelect : true
                    })

                    bot.approve(
                        message, `Added whitelist for [\`${ID}\`](${URL}) under **${member.user.tag}**`
                    )
                } catch (error) {
                    return bot.error(
                        message, 'whitelist add', error
                    )
                }
            }
        }
    }
}