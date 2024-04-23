const fs = require('fs');
const { MessageEmbed, Permissions } = require('discord.js');
const filepath = '/root/rewrite/Database/Moderation/warnings.json';
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'warn',
        aliases: [],
        description: 'Warn a server member.',
        syntax: 'warn <user> <reason>',
        example: 'warn @x6l Dork',
        permissions: 'manage_messages',
        parameters: 'user, reason',
        module: 'moderation'
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                        .setColor(session.warn)
                ]
            });
        }

        const targetUser = message.mentions.members.first();
        if (!targetUser) {
            return displayCommandInfo(module.exports, session, message);
        }
        const reason = args.slice(1).join(' ');
        let warnings = {};
        try {
            const data = fs.readFileSync(filepath, 'utf8');
            warnings = JSON.parse(data);
        } catch (error) {
            console.error('Error loading warnings from file:', error);
        }
        if (!warnings[message.guild.id]) {
            warnings[message.guild.id] = {};
        }
        if (!warnings[message.guild.id][targetUser.id]) {
            warnings[message.guild.id][targetUser.id] = [];
        }
        warnings[message.guild.id][targetUser.id].push(reason);
        try {
            fs.writeFileSync(filepath, JSON.stringify(warnings, null, 2));
        } catch (error) {
            console.error('Error saving warnings to file:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                ]
            });
        }

        message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor(session.green)
                    .setDescription(`${session.grant} ${message.author}: ${targetUser} has been warned for: **${reason}**`)
            ]
        });
    }
};
