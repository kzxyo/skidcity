module.exports = class Structure {
    constructor (Client) {
        this.Client = Client
    }

    async Start (Message, Command, Arguments) {
        const AllowedPermissions = []
        
        if (Command.Permissions) {
            this.Client.Database.query('SELECT * FROM fakepermissions WHERE guild_id = $1 AND permission = $2', {
                bind : [ Message.guild.id, Command.Permissions[0] ]
            }).then(async ([Results]) => {
                var Index = 0
                
                if (Results.length === 0) {
                    await this.Check(Message, Command, Arguments, AllowedPermissions)
                } else {
                    for (const Result of Results) {
                        ++Index
                        
                        if (Message.member.roles.cache.get(Result.role_id)) {
                            AllowedPermissions.push(Result.permission)
                        }
                        
                        if (Index === Results.length) {
                            await this.Check(Message, Command, Arguments, AllowedPermissions)
                        }
                    }
                }
            })
        } else {
            this.Check(Message, Command, Arguments, [])
        }
    }

    async Check (Message, Command, Arguments, AllowedPermissions) {
        if (Command.Permissions) {
            if (Command.Permissions.length > 1) {
                const DeniedPermissions = []

                for (const Permission of Command.Permissions) {
                    if (!AllowedPermissions.includes(Permission)) {
                        if (!Message.member.permissions.has(Permission)) DeniedPermissions.push(Permission)
                    }
                }

                if (DeniedPermissions.length > 0 || DeniedPermissions.length !== 0) {
                    return new this.Client.Response(
                        Message, `${DeniedPermissions.length > 1 ? 'Permissions' : 'Permission'} \`${DeniedPermissions.join(', ')}\` ${DeniedPermissions.length > 1 ? 'are' : 'is'} required to perform this command.`
                    )
                } else {
                    this.Invoke(Message, Command, Arguments)
                }
            } else {
                if (!AllowedPermissions.includes(Command.Permissions[0])) {
                    if (!Message.member.permissions.has(Command.Permissions[0])) {
                        return new this.Client.Response(
                            Message, `Permission \`${Command.Permissions[0].replace('And', 'and')}\` is required to perform this command.`
                        )
                    } else {
                        this.Invoke(Message, Command, Arguments)
                    }
                } else {
                    this.Invoke(Message, Command, Arguments)
                }
            }
        } else {
            this.Invoke(Message, Command, Arguments)
        }
    }

    async Invoke (Message, Command, Arguments) {
        Command.Invoke(this.Client, Message, Arguments)
    }
}