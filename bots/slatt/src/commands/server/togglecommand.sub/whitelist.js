const Subcommand = require('../../Subcommand.js');
const ReactionMenu = require('../../ReactionMenu.js');
const { MessageEmbed } = require('discord.js');

module.exports = class Check extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'togglecommand',
            name: 'whitelist',
            aliases: ['ignore', 'allow'],
            type: client.types.SERVER,
            usage: 'togglecommand whitelist <add/remove> <member> <command name>',
            description: 'Whitelist a certain member to use command',
        });
    }
    async run(message, args) {
        const client = message.client
        if (!args.length) return this.help(message)
        let subcommand
        let command = client.commands.get(args[2]) || client.aliases.get(args[2])
        let member = this.functions.get_member(message, args[1])
        if (command) subcommand = client.subcommands.get(`${command.name} ${args[3]}`) || client.subcommand_aliases.get(`${command.name} ${args[3]}`)
        switch (args[0]) {
            case 'add':
                if (subcommand) {
                    if (!member) return this.invalidUser(message)
                    const check = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}`, userID: member.id } })
                    if (!check) {
                        await client.db.command_whitelists.create({ guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}`, userID: member.id })
                        return this.send_success(message, `Whitelist **added** to member ${member} for subcommand **${command.name} ${subcommand.name}**`)
                    } else {
                        return this.send_error(message, 1, `Member ${member} is already whitelisted for subcommand **${command.name} ${subcommand.name}**`)
                    }
                } else if (command) {
                    if (!member) return this.invalidUser(message)
                    const check = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${command.name}`, userID: member.id } })
                    if (!check) {
                        await client.db.command_whitelists.create({ guildID: message.guild.id, cmd: `${command.name}`, userID: member.id })
                        return this.send_success(message, `Whitelist **added** to member ${member} for command **${command.name}**`)
                    } else {
                        return this.send_error(message, 1, `Member ${member} is already whitelisted for command **${command.name}**`)
                    }
                } else {
                    return this.send_error(message, 1, `Invalid **command or subcommand**. Use \`${message.prefix}help\` for a list`)
                }
            case 'remove':
                command = client.commands.get(args[2]) || client.aliases.get(args[2])
                if (command) subcommand = client.subcommands.get(`${command.name} ${args[3]}`) || client.subcommand_aliases.get(`${command.name} ${args[3]}`)
                if (subcommand) {
                    if (!member) return this.invalidUser(message)
                    const check = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}`, userID: member.id } })
                    if (check) {
                        await client.db.command_whitelists.destroy({where: { guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}`, userID: member.id }})
                        return this.send_success(message, `Whitelist **removed** from member ${member} for subcommand **${command.name} ${subcommand.name}**`)
                    } else {
                        return this.send_error(message, 1, `Member ${member} is not whitelisted for subcommand **${command.name} ${subcommand.name}**`)
                    }
                } else if (command) {
                    if (!member) return this.invalidUser(message)
                    const check = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${command.name}`, userID: member.id } })
                    if (check) {
                        await client.db.command_whitelists.destroy({where:{ guildID: message.guild.id, cmd: `${command.name}`, userID: member.id }})
                        return this.send_success(message, `Whitelist **removed** from member ${member} for command **${command.name}**`)
                    } else {
                        return this.send_error(message, 1, `Member ${member} is not whitelisted for command **${command.name}**`)
                    }
                } else {
                    return this.send_error(message, 1, `Invalid **command or subcommand**. Use \`${message.prefix}help\` for a list`)
                }
            default:
                return this.help(message)
        }
    }
};