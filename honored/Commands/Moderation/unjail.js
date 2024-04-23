const { Permissions, MessageEmbed } = require("discord.js");
const unjailrolePath = '/root/rewrite/Database/Moderation/jailsystem.json';
const displayCommandInfo = require('/root/rewrite/Utils/command.js');
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'unjail',
        aliases: ['unprison'],
        description: 'Release a user from the shackles',
        syntax: 'unjail [user]',
        example: 'unjail @x6l',
        module: 'moderation',
        devOnly: false
    },
    run: async (session, message, args) => {
        const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                    .setColor(session.warn)
            ]
        });

        let unjailData = {};
        try {
            unjailData = JSON.parse(fs.readFileSync(unjailrolePath, 'utf8'));
        } catch (error) {
            console.error('Error reading unjail role data:', error);
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: An error occured please contact support`)
            ]});
        }

        const jailRoleId = unjailData[message.guild.id];
        if (!jailRoleId) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: The jail role has not been set, set one using \`unjailrole @role\``)
        ]});

        const jailrole = message.guild.roles.cache.find(role => role.name === 'jailed');
        if (!jailrole) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: The jail role has not been set`)
        ]});

        if (!user) {
            return displayCommandInfo(module.exports, session, message);
        }

        if (user === message.member) return message.channel.send({ embeds: [
            new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: You can't jail yourself`)
        ]});
        if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`You can't jail someone above you`);
        
        try {
            await user.roles.remove(jailrole);
            await user.roles.add(jailRoleId);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.green)
                    .setDescription(`${session.grant} ${message.author}: ${user} has been unjailed`)
            ]});
        } catch (error) {
            console.error('Error unjailing user:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: An error occured please contact support`)
            ]});
        }
    }
};
