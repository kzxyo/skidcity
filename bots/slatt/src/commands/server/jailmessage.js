const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const db = require("quick.db")

module.exports = class BanCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'jailmessage',
            usage: 'jailmessage <content>',
            type: client.types.MOD,
            description: `sets a jail message, use 'variables' command for variables `,
            clientPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            userPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            subcommands: ['jailmessage']
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message);
        }
        let jailmsg = await message.client.db.jail_message.findOne({where: {guildID: message.guild.id}})
        let jailMessage = args.join(' ')
        if(jailmsg === null) {
            await message.client.db.jail_message.create({guildID: message.guild.id, message: jailMessage})

        } else {
           await message.client.db.jail_message.update({message: jailMessage}, {where: {guildID: message.guild.id}})
        }
        this.send_success(message, `Jail message updated: ${jailMessage}`)
        message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated jail message`)
    }
};