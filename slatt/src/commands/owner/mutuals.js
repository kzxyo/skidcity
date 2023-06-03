const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class GuildBannerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'mutuals',
            aliases: ["m"],
            description: 'show a users mutual servers',
            subcommands: [`mutuals <user>`],
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        message.client.users.fetch(args[0] || message.author.id).then(u => {
            let user = u
            let info = `**id:** \`${user.id}\`\n**username:** \`${user.username}\`\n**bot:** \`${user.bot}\`\n**discrim:** \`${user.discriminator}\`\n**avatar:** [link](https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}?size=512)`
            let num = 0
            let guilds = message.client.guilds.cache.filter(guild => !!guild.members.cache.get(user))
            let list = guilds.map(g => `\`${++num}.\` **${g.name}** | ${g.id}`)
            const embed = new MessageEmbed()
                .setTitle('Mutual Servers')
                .addField('User Info', info, true)
                .setTimestamp()
                .setFooter(`${guilds.size} mutuals`)
                .setColor(message.guild.me.displayHexColor);
            if (list.length <= 10) {
                const range = (list.length == 1) ? '[1]' : `[1 - ${list.length}]`;
                message.channel.send(embed.setTitle(`Mutual Servers ${range}`).setDescription(list.join('\n')));
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, list);
            }
        })
    }
}