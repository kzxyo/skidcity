module.exports = class Command {
    constructor (Client, Name, Options) {
        this.Client = Client
        this.Name = Name

        this.Aliases = Options.Aliases ? Options.Aliases : null
        this.Syntax = Options.Syntax ? Options.Syntax : null
        this.Arguments = Options.Arguments ? Options.Arguments : null
        this.Permissions = Options.Permissions ? Options.Permissions : null
        this.Commands = Options.Commands ? Options.Commands : null
        this.Module = Options.Module ? Options.Module : null
    }
}
