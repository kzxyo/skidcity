const { MessageEmbed } = require("discord.js");
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'invites',
        aliases: ['inv'],
        description: 'Shows the invites of the server.',
        syntax: 'invites',
        example: 'invites',
        module: 'information',
        devOnly: false
    },

    run: async (session, message, args) => {
        const invites = await message.guild.invites.fetch();
        if (invites.size === 0) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no invites in this server`)
            ]});
        }

        const pages = [];
        let count = 0;
        let embedDescription = '';
        invites.each(invite => {
            const inviteCreator = invite.inviter;
            const inviteCode = invite.code;
            const uses = invite.uses;
            count++;
            embedDescription += `\`${count}.\` ${inviteCreator} **[${inviteCode}](https://discord.gg/${inviteCode})** - ${uses} uses\n`;
            if (count % 10 === 0 || count === invites.size) {
                const embed = new MessageEmbed()
                    .setColor(session.color)
                    .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                    .setTitle(`Invites list`)
                    .setDescription(embedDescription);
                pages.push(embed);
                embedDescription = '';
            }
        });

        if (pages.length > 1) {
            pagination(session, message, pages, 1);
        } else {
            message.channel.send({ embeds: pages });
        }
    }
}
