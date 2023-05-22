const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');


module.exports = class GuildBannerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'guildbanner',
            aliases: ['gb', 'serverbanner'],
            usage: `guildbanner [id]`,
            usage: 'sends the guildbanner',
            type: client.types.INFO,
            subcommands: ['guildbanner']
        });
    }
    async run(message, args) {
        let guild = message.client.guilds.cache.get(args[0]) || message.guild
        if (!guild) {
            return this.send_error(message, 1, `i am not in the guild you provided`)
        }
        if(!guild.bannerURL()) {
            return this.send_error(message, 1, `${guild.name} does not have a guild banner`)
        }
        const embed = new MessageEmbed()
            .setTitle(`${guild.name}'s banner`)
            .setImage(guild.bannerURL())
            .setColor(this.hex)
        message.channel.send({ embeds: [embed] });
    }
}