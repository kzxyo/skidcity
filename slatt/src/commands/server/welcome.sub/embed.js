const Subcommand = require('../../Subcommand.js');

module.exports = class Message extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'welcome',
            name: 'embed',
            type: client.types.SERVER,
            usage: 'welcome embed [embed] or "none"',
            description: 'Update your servers welcome message to an embed',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        let check = await message.client.db.welcome_message.findOne({ where: { guildID: message.guild.id } })
        let embed = await message.client.db.welcome_embed.findOne({ where: { guildID: message.guild.id } })
        if (check !== null) {
            return this.send_error(message, 1, `you may not have a welcome message, and embed at the same time, clear one to proceed`)
        }
        if (args[0].toLowerCase() === 'none') {
            if (embed === null) {
                return this.send_error(message, 1, `There is no **welcome embed** for this server`)
            } else {
                await message.client.db.welcome_embed.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **welcome embed** has been removed`)
            }
        }
        if (check === null) {
            await message.client.db.welcome_embed.create({
                guildID: message.guild.id,
                code: args.join(" ")
            })
        } else {
            return this.send_success(message, `Use \`${prefix.prefix}welcome embed none\` to clear and update your embed`)
        }
        return this.send_success(message, `Your welcome embed has been updated, use \`${prefix.prefix}welcome check\`\nUse \`${prefix.prefix}welcome embed none\` to clear and update it.`)
    }
}