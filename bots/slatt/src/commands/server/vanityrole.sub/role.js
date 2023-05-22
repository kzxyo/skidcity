const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')

module.exports = class role extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'vanityrole',
            name: 'role',
            type: client.types.SERVER,
            usage: 'vanityrole role [role] or "none"',
            description: 'Update your servers vanity role',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        let check = await message.client.db.vanity_role.findOne({ where: { guildID: message.guild.id } })
        const role = await this.functions.get_role(message, args.join(' '))
        if (args[0] === 'none') {
            if (check) {
                await message.client.db.vanity_role.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `Vanity role has been removed`)
            } else {
                return this.send_error(message, 1, `I could not find a Vanity role to remove`)
            }
        }
        if (check === null) {
            await message.client.db.vanity_role.create({
                guildID: message.guild.id,
                role: role.id
            })
        } else {
            await message.client.db.vanity_role.update({ role: role.id }, {
                where: { guildID: message.guild.id }
            })
        }
        return this.send_success(message, `Vanity role has been set to **${role}**`)
    }
}