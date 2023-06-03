const Command = require('../Command.js');
const {
    Util: {
        cloneObject
    }
} = require("discord.js");


module.exports = class LeaveGuildCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'sudo',
            usage: `sudo [user] [command] [args]`,
            aliases: ["cloneobject", "cloneobj", 'cobj'],
            subcommands: [`sudo`],
            description: 'Run a command as another member',
            type: client.types.OWNER,
            ownerOnly: true,

        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        const member = this.functions.get_member(message, args[0])
        if (!member) {
            return this.invalidUser(message)
        }
        let command = message.client.commands.get(args[1]) || message.client.aliases.get(args[1])
        let subcommand = message.client.subcommands.get(args[2]) || message.client.subcommand_aliases.get(args[2])
        if (subcommand) {
            const msg = cloneObject(message);
            msg.author = member.user;
            Object.defineProperty(msg, "member", {
                value: member
            });
            msg.content = `${prefix.prefix}${subcommand.base} ${subcommand.name} ${args.slice(2).join(' ')}`;
            this.client.emit("messageCreate", msg);
         } else {
            const msg = cloneObject(message);
            msg.author = member.user;
            Object.defineProperty(msg, "member", {
                value: member
            });
            msg.content = `${prefix.prefix}${command.name} ${args.slice(2).join(' ')}`;
            this.client.emit("messageCreate", msg);
        }
    }
}