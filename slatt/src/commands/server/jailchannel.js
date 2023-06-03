const Command = require('../Command.js');
const db = require("quick.db")

module.exports = class BanCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'jailchannel',
            usage: 'jailchannel <channel>',
            type: client.types.SERVER,
            description: `sets a jail channel, will overwrite the default one called 'jail'`,
            clientPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            userPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            subcommands: ['jailchannel']
        });
    }
    async run(message, args) {
        const dbjailrole = await message.client.db.jail_role.findOne({ where: { guildID: message.guild.id } })
        var jailrole = message.guild.roles.cache.get(dbjailrole ? dbjailrole.role : null) || message.guild.roles.cache.find(r => r.name === "Jailed")
        var jail_channel = await message.client.db.jail_channel.findOne({ where: { guildID: message.guild.id } })
        if (!args.length) {
            return this.help(message);
        }
        let jailchannel = await this.functions.get_channel(message, args.join(' '))
        if (!jailchannel) {
            return this.send_error(message, 0, `provide a valid channel in this server`);
        }
        if (jail_channel === null) {
            await message.client.db.jail_channel.create({ guildID: message.guild.id, channel: jailchannel.id })
        } else {
            await message.client.db.jail_channel.update({ channel: jailchannel.id }, { where: { guildID: message.guild.id } })
        }
        message.guild.channels.cache.filter(c => c === jailchannel).forEach(async (channel, id) => {
            await channel.createOverwrite(jailrole, {
                SEND_MESSAGES: true,
                VIEW_CHANNEL: true
            })
            await channel.createOverwrite(message.guild.id, {
                SEND_MESSAGES: false,
                VIEW_CHANNEL: false
            });
             this.send_success(message, `jail channel was set, and permissions were updated for **${jailchannel}**`)
             message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated jail channel to ${jailchannel}`)
        })
    }
}