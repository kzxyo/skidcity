const { Permissions, MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'kick',
        aliases: ['k'],
        description: 'Kicks mentioned user.',
        syntax: 'kick [user] (reason)',
        example: 'kick @x6l bad',
        permissions: 'kick_members',
        parameters: 'user, reason',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        let reason = args.slice(1).join(" ");

        if (!reason) reason = 'No Reason';

        if (!args[0]) return displayCommandInfo(module.exports, session, message);

        if (!message.member.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`kick_members\``)
                    .setColor(session.warn)
            ]
        });

        if (!message.guild.me.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: I'm **missing** permission: \`kick_members\``)
                    .setColor(session.warn)
            ]
        });

        if (!user) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You didn't mention a user `)
                    .setColor(session.warn)
            ]
        });

        if (user === message.member) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You can't kick yourself`)
                    .setColor(session.warn)
            ]
        });

        if (user === session.user.id) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: try one more time i swear it will work`)
                    .setColor(session.warn)
            ]
        });

        if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You cant kick someone above you`)
                    .setColor(session.warn)
            ]
        });

        if (!user.kickable) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: I can't kick someone above me`)
                    .setColor(session.warn)
            ]
        });

        const userembed = new MessageEmbed()
        .setColor(session.color)
        .setTitle('Kicked')
        .addFields(
            { name: 'You have been kicked in', value: message.guild.name, inline: true },
            { name: 'Moderator', value: message.author.username, inline: true },
            { name: 'Reason', value: reason, inline: false }
        )
        .setThumbnail(message.guild.iconURL({ dynamic: true }))
        .setFooter('If you would like to dispute this punishment, contact a staff member.')
        .setTimestamp();

        user.send({ embeds: [userembed] }).catch(err => console.log(err));

        user.kick({ reason: `${reason}` }).then(() => {
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.grant} ${message.author}: I have kicked that user`)
                        .setColor(session.green)
                ]
            });
        }).catch(err => console.log(err));
    }
};
