module.exports = class Event {
    constructor (bot, name, options = {}) {
        this.bot = bot
        this.name = name
        this.once = options.once ?? null

        this._listener = this._execute.bind(this)
    }

    async _execute (...body) {
        try {
            await this.execute(
                this.bot, ...body
            )
        } catch (error) {
            console.error(error)
        }
    }

    startListener () {
        this.once ? this.bot.once(
            this.name, this._listener
        ) : this.bot.on(
            this.name, this._listener
        )
    }

    stopListener () {
        this.bot.off(
            this.name, this._listener
        )
    }
}

