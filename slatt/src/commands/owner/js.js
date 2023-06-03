const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const { get } = require('axios')

module.exports = class LeaveGuildCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'js',
            aliases: ["docs"],
            usage: `docs [query]`,
            description: 'Searches the discord.js docs',
            type: client.types.OWNER,
            ownerOnly: true,

        });
    }
    async run(message, args) {
        const url = `https://djsdocs.sorta.moe/v2/embed?src=stable&q=${encodeURIComponent(args)}`;
        get(url).then(({
            data
        }) => {
            if (data && !data.error) {
                message.channel.send({
                    embed: data
                });
            } else {
                return
            }
        }).catch(err => {
            console.log(err)
        });
    }
}