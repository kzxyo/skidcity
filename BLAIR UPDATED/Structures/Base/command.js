module.exports = class Command {
    constructor (bot, name, parameters = {}) {
        this.bot = bot
        this.name = name
        this.description = parameters.description ?? null
        this.permissions = parameters.permissions ?? null
        this.parameters = parameters.parameters ?? null
        this.cooldown = parameters.cooldown ?? null
        this.syntax = parameters.syntax ?? null
        this.example = parameters.example ?? null
        this.aliases = parameters.aliases ?? null
        this.flags = parameters.flags ?? null
        this.commands = parameters.commands ?? null
        this.module = parameters.module ?? 'Miscellaneous',
        this.guarded = parameters.guarded ?? null
    }
}