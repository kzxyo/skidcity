const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class GuildIconCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'guildicon',
            aliases: ['gi', 'gicon', 'guildi', 'sicon', 'servericon'],
            usage: `guildicon [id]`,
            usage: 'sends the guildicon of your/or a server the bot is in',
            type: client.types.INFO,
            subcommands: ['guildicon']
        });
    }
    async run(message, args) {
        let guild = message.client.guilds.cache.get(args[0]) || message.guild
        if (!guild) {
            return this.send_error(message, 1, `i am not in the guild you provided`)
        }
        const embed = new MessageEmbed()
            .setTitle(`${guild.name}'s Icon`)
            .setImage(guild.iconURL({
                dynamic: true,
                size: 512
            }))
            .setColor(this.hex);
        message.channel.send({ embeds: [embed] });
    }
}