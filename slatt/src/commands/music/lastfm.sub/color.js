const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'color',
            type: client.types.LASTFM,
            usage: 'lastfm color [hexcode]',
            description: 'Update your last.fm embed color',
        });
    }
    async run(message, args) {
        let color = await message.client.db.lf_color.findOne({ where: { userID: message.author.id } })
        let rColor = args[0]
        if (!rColor && color !== null) {
            await message.client.db.lf_color.destroy({ where: { userID: message.author.id } })
            return this.send_success(message, `Your last.fm embed color has been **reset**, and will display as **#303135**`)
        }
        if (!rColor.includes('#')) return this.send_error(message, 1, 'provide a valid hexcode: \`#11111\`');
        if (color !== null) {
            await message.client.db.lf_color.update({ color: rColor }, { where: { userID: message.author.id } })
        } else {
            await message.client.db.lf_color.create({ userID: message.author.id, color: rColor })

        }
        return this.send_info(message, `Your last.fm embed color has been updated to **${rColor}**`)

    }
}