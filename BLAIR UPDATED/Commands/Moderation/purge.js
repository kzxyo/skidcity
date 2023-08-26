const Command = require('../../Structures/Base/command.js')

module.exports = class Purge extends Command {
    constructor (bot) {
        super (bot, 'purge', {
            description : 'Purge',
            permissions : [ 'ManageMessages' ]
        })
    }

    async execute (bot, message, args) {
        try {
            if (!args[0]) {
                return bot.help(
                    message, this
                )
            }

            const input = parseInt(args[0])
                    
                    let amount;
                    
                    if (input === 0) {
                        amount = 1
                    } else if (input > 1000) {
                        amount = 1000
                    } else {
                        amount = input
                    }

                    const purger = new Purger(message.channel, amount)

                    await message.delete()
                    purger.construct()
        } catch (error) {
            return bot.error(
                message, 'purge', error
            )
        }
    }
}

class Purger {
    constructor (channel, amount, condition = () => true) {
        this.channel = channel
        this.amount = amount
        this.condition = condition
        this.processed = 0
    }

    async construct () {
        this.messages = await this.fetch()

        await this.next()
    }

    async next () {
        while (this.processed < this.amount && this.messages.size > 0) {
            await this.purge()

            this.messages = await this.fetch(this.messages.last().id)
        }
    }

    async fetch (before = null) {
        const messages = await this.channel.messages.fetch({
            limit : 100,
            before : before
        })

        return messages.filter((message) => this.condition(message))
    }

    async purge () {
        const del = this.messages.map((message) => message).slice(0, this.amount - this.processed)

        const IDs = del.map((message) => message.id)

        await this.channel.bulkDelete(IDs)

        this.processed += del.length
    }
}