const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const db = require("quick.db")

module.exports = class BanCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'jailrole',
            usage: 'jailrole <role>',
            type: client.types.SERVER,
            description: `sets a jail role, will overwrite the default role created called 'Jailed'`,
            clientPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            userPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            subcommands: ['jailrole']
        });
    }
    async run(message, args) {
        const jail_role = await message.client.db.jail_role.findOne({ where: { guildID: message.guild.id } })
        let dbjail = await message.client.db.jail_channel.findOne({ where: { guildID: message.guild.id } })
        let jail = message.guild.channels.cache.get(dbjail ? dbjail.channel : null) || message.guild.channels.cache.find(channel => channel.name === "jail")
        if (!args.length) {
            return this.help(message);
        }
        let jailrole = this.functions.get_role(message, args.join(' '))
        if (!jailrole) {
            return this.send_error(message, 0, `provide a valid role in this server`);
        }
        if (jail_role === null) {
            await message.client.db.jail_role.create({ guildID: message.guild.id, role: jailrole.id })
        } else {
            await message.client.db.jail_role.update({ role: jailrole.id }, { where: { guildID: message.guild.id } })
        }
        jailrole.setPermissions([])
        message.guild.channels.cache.forEach(async (channel, id) => {
            await channel.createOverwrite(jailrole, {
                SEND_MESSAGES: false,
                VIEW_CHANNEL: false
            });
            if (channel === jail) {
                channel.createOverwrite(jailrole, {
                    SEND_MESSAGES: true,
                    VIEW_CHANNEL: true
                })
            }
        })
        this.send_success(message, `jail role updated, permissions were set for ${jailrole}`)
        message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated jail role to ${jailrole}`)

    }
};