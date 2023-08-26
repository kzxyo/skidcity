const Command = require('../../Structures/Base/command.js')

const commands = [ 'set' ]

module.exports = class Starboard extends Command {
    constructor (bot) {
        super (bot, 'starboard', {
            description : 'Showcase the best messages',
            permissions : [ 'ManageGuild' ],
            syntax : '(command) <arguments>',
            example : 'set #board',
            aliases : [ 'star', 'sb' ],
            commands : [
                {
                    name : 'starboard set',
                    description : 'Set the Starboard channel',
                    permissions : [ 'ManageGuild' ],
                    parameters : [ 'channel' ],
                    syntax : `<channel>`,
                    example : '#board'
                }
            ],
            module : 'Starboard'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !commands.includes(command)) {
            return bot.help(message, this)
        }

        switch (command) {
            case ('set') : {
                try {
                    const channel = args[1] ? await bot.converters.channel(
                        message, args.slice(1).join(' '), {
                            response : true,
                            type : 0
                        }
                    ) : message.channel

                    if (!channel) {
                        return
                    }
                } catch (error) {
                    return bot.error(
                        message, 'starboard set', error
                    )
                }
            }
        }
    }
}