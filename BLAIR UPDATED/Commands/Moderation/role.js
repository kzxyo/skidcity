const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const commands = []

module.exports = class Role extends Command {
    constructor (bot) {
        super (bot, 'role', {
            description : 'Add or remove a role to/from a member',
            permissions : [ 'ManageRoles' ],
            parameters : [ 'member', 'roles' ],
            syntax : '(member) (role)',
            example : `${bot.owner.username} @Friends`,
            aliases : [ 'r' ],
            module : 'Moderation'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0]) {
            return bot.help(
                message, this
            )
        }

        if (commands.includes(command)) {
            switch (true) {

            }
        } else {
            try {
                const member = await bot.converters.member(message, args[0], { response : true })

                if (!member) {
                    return
                }

                if (!args[1]) {
                    return bot.warn(message, `Mention a role to **add** or **remove**`)
                }

                if (args.slice(1).join(' ').split(',').length === 1 || args.slice(1).join(' ').endsWith(',')) {
                    const role = await bot.converters.role(message, args.slice(1).join(' '), { response : true })

                    if (!role) {
                        return
                    }

                    const validate = await bot.validators.role(message, role, { response : true })

                    if (!validate) {
                        return
                    }

                    if (member.roles.cache.has(role.id)) {
                        await member.roles.remove(role.id, `${message.author.tag}: Removed Role`)

                        bot.approve(
                            message, `Removed ${role} from ${member}`
                        )
                    } else {
                        await member.roles.add(role.id, `${message.author.tag}: Added Role`)

                        bot.approve(
                            message, `Added ${role} to ${member}`
                        )
                    }
                } else {
                    const success = [], failure = []

                    for (let str of args.slice(1).join(' ').split(', ')) {
                        str = str.trim().startsWith('<@&') ? str.replace('<@&', '').replace('>', '').trim() : str.trim()

                        const role = message.guild.roles.cache.get(str) || message.guild.roles.cache.find((role) => role.name.toLowerCase().includes(str.toLowerCase()))

                        if (role) {
                            let eligible = true

                            switch (true) {
                                case message.author.id !== message.guild.ownerId && message.member.roles.highest.position <= role.position :
                                    eligible = false
                                case message.guild.members.cache.get(bot.user.id).roles.highest.position === role.position || message.guild.members.cache.get(bot.user.id).roles.highest.position < role.position :
                                    eligible = false
                                case role.managed :
                                    eligible = false
                                case role.id === message.guild.roles.everyone.id :
                                    eligible = false
                                break
                              }

                            if (eligible) {
                                success.push({ role : role.id, type : member.roles.cache.has(role.id) ? 'remove' : 'add' })
                            } else {
                                failure.push({ role : role.id, type : member.roles.cache.has(role.id) ? 'remove' : 'add' })
                            }
                        }
                    }

                    if (!success.length) {
                        return bot.warn(
                            message, `You can't **add or remove** any of the roles`
                        )
                    }

                    const changed = await Promise.all((success.map(async (role) => {
                        if (role.type === 'add') {
                            await member.roles.add(role.role)

                            return `+${message.guild.roles.cache.get(role.role).name}`
                        } else if (role.type === 'remove') {
                            await member.roles.remove(role.role)

                            return `-${message.guild.roles.cache.get(role.role).name}`
                        }
                    })))

                    bot.approve(
                        message, `Updated roles for ${member}: **${changed.join(' ')}**`
                    )                
                }
            } catch (error) {
                return bot.error(
                    message, 'role', error
                )
            }
        }
    }
}