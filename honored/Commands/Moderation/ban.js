const { Permissions, MessageActionRow, MessageButton, MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'ban',
        aliases: [],
        description: 'Banishes a server member.',
        syntax: 'ban <user> <reason>',
        example: 'ban @x6l bad boy',
        permissions: 'ban_members',
        parameters: 'user, reason',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        let reason = args.slice(1).join(" ");
        if (!reason) reason = 'No Reason';

        if (!args[0]) return displayCommandInfo(module.exports, session, message);

        if (!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`ban_members\``)
                    .setColor(session.warn)
            ]
        });

        if (!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: I'm **missing** permission: \`ban_members\``)
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
                    .setDescription(`${session.mark} ${message.author}: You can't ban yourself`)
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
                    .setDescription(`${session.mark} ${message.author}: You cant ban someone above you`)
                    .setColor(session.warn)
            ]
        });

        if (!user.bannable) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: I can't ban someone above me`)
                    .setColor(session.warn)
            ]
        });

        const userembed = new MessageEmbed()
            .setColor('#dc2c44')
            .setTitle('Banned')
            .addFields(
                { name: 'You have been banned in', value: message.guild.name, inline: true },
                { name: 'Moderator', value: message.author.username, inline: true },
                { name: 'Reason', value: reason, inline: false }
            )
            .setThumbnail(message.guild.iconURL({ dynamic: true }))
            .setFooter('If you would like to dispute this punishment, contact a staff member.')
            .setTimestamp();

        if (user.premiumSince) {
            const warningEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`Are you sure you want to ban ${user.user.tag}?\n> This user is a server booster!`);

            const row = new MessageActionRow()
                .addComponents(
                    new MessageButton()
                        .setCustomId('accept')
                        .setLabel('Accept')
                        .setStyle('SUCCESS'),
                    new MessageButton()
                        .setCustomId('reject')
                        .setLabel('Reject')
                        .setStyle('DANGER')
                );

            const warningMessage = await message.channel.send({ embeds: [warningEmbed], components: [row] });

            const filter = i => i.user.id === message.author.id;

            const collector = message.channel.createMessageComponentCollector({ filter, time: 15000 });

            collector.on('collect', async i => {
                if (i.customId === 'accept') {
                    await user.send({ embeds: [userembed] }).catch(err => console.log(err));
                    await user.ban({ reason: `${reason}` }).then(() => {
                        message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setDescription(`${session.grant} ${message.author}: I have banned that user`)
                                    .setColor(session.green)
                            ]
                        });
                    }).catch(err => console.log('Couldnt dm that user'));
                } else if (i.customId === 'reject') {
                    warningMessage.delete();
                }
            });

            collector.on('end', () => {
                warningMessage.delete();
            });
        } else {
            await user.send({ embeds: [userembed] }).catch(err => console.log(err));
            await user.ban({ reason: `${reason}` }).then(() => {
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: **${user.user.username}** has been banned from the server`)
                            .setColor(session.green)
                    ]
                });
            }).catch(err => console.log('Couldnt dm that user'));
        }
    }
};
