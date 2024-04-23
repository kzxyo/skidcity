const { Permissions, MessageEmbed } = require("discord.js");
const unjailrolePath = '/root/rewrite/Database/Moderation/jailsystem.json';
const displayCommandInfo = require('/root/rewrite/Utils/command.js');
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'unjailrole',
        aliases: ['ujr'],
        description: 'Set the jail role for unjailing users',
        usage: 'unjailrole [@role]',
        module: 'moderation',
        devOnly: false
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                    .setColor(session.warn)
            ]
        });


        const role = message.mentions.roles.first();
        if (!role) return displayCommandInfo(module.exports, session, message);

        let unjailData = {};
        try {
            unjailData = JSON.parse(fs.readFileSync(unjailrolePath, 'utf8'));
        } catch (error) {
            console.error('Error reading unjail role data:', error);
        }

        unjailData[message.guild.id] = role.id;

        fs.writeFileSync(unjailrolePath, JSON.stringify(unjailData, null, 4));

        message.channel.send({ embeds: [
            new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: The jail role has been set to ${role}`)
        ]});
    }
};
