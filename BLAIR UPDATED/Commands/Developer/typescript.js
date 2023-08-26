const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

module.exports = class JavaScript extends Command {
    constructor (bot) {
        super (bot, 'javascript', {
            aliases : [ 'js' ],
            module : 'Developer',
            guarded : true
        })
    }

    async execute (bot, message, args, prefix) {
        if (message.author.id !== '944099356678717500') return

        const script = args.join(' ').replace('```', '')

        try {
            var evaluated

            try {
                evaluated = await eval(script)
            } catch (error) {
                console.error(error)
                return message.react('‼️')
            }

            if (typeof evaluated !== 'string') evaluated = require('util').inspect(evaluated)
            
            message.react('✅')

            if (evaluated.length > 2000) {
                const buffer = Buffer.from(evaluated, 'utf-8')

                message.channel.send({
                    files : [
                        new Discord.AttachmentBuilder(buffer, {
                            name : 'code.txt'
                        })
                    ]
                })
            } else {
                message.channel.send(evaluated)
            }
        } catch (error) {
            return new bot.error(
                message, 'evaluate', error
            )
        }
    }
}

