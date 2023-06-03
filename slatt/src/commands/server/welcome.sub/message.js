const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const db = require('quick.db')
module.exports = class Message extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'welcome',
            name: 'message',
            aliases: ['msg'],
            type: client.types.SERVER,
            usage: 'welcome message [msg]',
            description: 'Update your servers welcome message',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        let check = await message.client.db.welcome_message.findOne({ where: { guildID: message.guild.id } })
        let embed = await message.client.db.welcome_embed.findOne({ where: { guildID: message.guild.id } })
        if (embed !== null) {
            return this.send_error(message, 1, `you may not have a welcome message, and embed at the same time, clear one to proceed`)
        }
        if (args[0].toLowerCase() === 'none') {
            if (check === null) {
                return this.send_error(message, 1, `There is no **welcome message** for this server`)
            } else {
                await message.client.db.welcome_message.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **welcome message** has been removed`)
            }
        }
        if (check === null) {
            await message.client.db.welcome_message.create({
                guildID: message.guild.id,
                message: args.join(" ")
            })
        } else {
            await message.client.db.welcome_message.update({ message: args.join(' ') }, { where: { guildID: message.guild.id } })
        }
        return this.send_success(message, `Your welcome message has been updated, use \`${prefix.prefix}welcome check\``)
    }
}