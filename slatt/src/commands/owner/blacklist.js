const Discord = require("discord.js")
const db = require("quick.db")
const Command = require('../Command.js');

module.exports = class BlastCommand extends Command {
    constructor(client) {
        super(client, {
            name: "blacklist",
            aliases: ["bl"],
            description: `blacklist a user`,
            subcommands: [`blacklist add <user>`, `blacklist remove <user>`, `blacklist id <userid>`],
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        if (!args.length)
            return this.invalidArgs(message, 'provide a valid user')
        message.guild.members.fetch({
                query: args[1],
                limit: 1
            })
            .then(members => {
                const user = members.first() || message.mentions.members.first() || message.guild.members.cache.get(args[1]) || message.guild.members.cache.find(x => x.user.tag === args[1] || x.user.tag === args[1])
                if (args[0].toLowerCase() === "add") {
                    db.set(`bl_${user.id}`, true)
                    return this.send_success(message, `${user} has been blacklisted`)
                } else if (args[0].toLowerCase() === "remove") {
                    db.delete(`bl_${user.id}`)
                    return this.send_success(message, `${user} has been unblacklisted`)
                } else if (args[0].toLowerCase() === "guild") {
                    const guild = args[1]
                    if(isNaN(guild)) return this.send_error(message, 1, `Provide a guild id`)
                        db.set(`guildBlacklist_${args[1]}`, true)
                        return this.send_success(message, `**${args[1]}** has been guild blacklisted`)
                } else if (args[0].toLowerCase() === "id") {
                    message.client.users.fetch(args[1]).then(u => {
                        db.set(`bl_${u.id}`, true)
                        return this.send_success(message, `**${u.username}#${u.discriminator}** has been blacklisted`)
                    })
                }
            })
    }
}