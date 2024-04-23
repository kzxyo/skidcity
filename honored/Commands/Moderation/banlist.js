const { MessageEmbed, Permissions } = require("discord.js");
const pagination = require('/root/rewrite/Utils/paginator.js');


module.exports = {
    configuration: {
        commandName: 'banlist',
        aliases: ['bans'],
        description: 'Shows all banned users in the server',
        syntax: 'banlist',
        example: 'banlist',
        permissions: 'ban_members',
        module: 'moderation'
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`ban_members\``)
                        .setColor(session.warn)
                ]
            });
        }

        const bans = await message.guild.bans.fetch();
        const bannedUsers = bans.map(ban => ban.user);

        if (bannedUsers.length === 0) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: There are no banned users in this server`)
                ]
            });
        }

        if (bannedUsers.length <= 10) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Banned users list`)
                .setDescription(bannedUsers.map(user => `<@${user.id}>`).join('\n'));

            return message.channel.send({ embeds: [embed] });
        }

        const pages = [];
        for (let i = 0; i < bannedUsers.length; i += 10) {
            const current = bannedUsers.slice(i, i + 10);
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Banned users list`)
                .setDescription(current.map(user => `<@${user.id}>`).join('\n'));
            pages.push(embed);
        }

        pagination(session, message, pages, 1);
    }
};