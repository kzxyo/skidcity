const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const rgx = /^(?:<@!?)?(\d+)>?$/;

module.exports = class LeaveGuildCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'createinvite',
            aliases: ["invitemeto", "createinv", "create"],
            usage: `createinvite <server>`,
            type: client.types.OWNER,
            ownerOnly: true,

        });
    }
    async run(message, args) {
        let guild = null;
        if (!args[0]) return message.channel.send("s")
        if (args[0]) {
            let fetched = message.client.guilds.cache.find(g => g.name.toLowerCase().includes(args.join(' ').toLowerCase()));
            let found = message.client.guilds.cache.get(args[0]);
            if (!found) {
                if (fetched) {
                    guild = fetched;
                }
            } else {
                guild = found
            }
        } else {
           return this.help(message)
        }
        if (guild) {
            let tChannel = guild.channels.cache.find(ch => ch.type == "GUILD_TEXT" && ch.permissionsFor(ch.guild.me).has("CREATE_INSTANT_INVITE"));
            if (!tChannel) {
                return message.channel.send("no channels to create invite");
            }
            let invite = await tChannel.createInvite({
                temporary: false,
                maxAge: 0
            }).catch(err => {
                return message.channel.send(`${err}`);
            });
            message.channel.send(invite.url);
        } else {
            return message.channel.send(`**${message.client.user.username}** is not in **${args.join(' ')}**`);
        }
    }
}