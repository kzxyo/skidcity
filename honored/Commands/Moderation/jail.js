const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'jail',
        aliases: ['prison'],
        description: 'Jails the specified member (sets up upon first use)',
        syntax: 'jail [user] (reason)',
        example: 'jail @x6l bad',
        parameters: 'user, reason',
        permissions: 'manage_roles',
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

        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }

        const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        let jailrole = message.guild.roles.cache.find(role => role.name === 'jailed');
        let jailchannel = message.guild.channels.cache.find(c => c.name === 'jail');

        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`This command requires \`manage messages\` permission`);
        if (!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`This command requires me to have \`manage messages\` permission`);
        if (!user) return message.channel.send(`I couldn't find any members with that name`);

        if (!jailrole) {
            try {
                jailrole = await message.guild.roles.create({
                    name: 'jailed',
                    color: 'DEFAULT',
                }).then(() => {
                    message.channel.send('Setting up jail for the first time..');
                });
            } catch {
                message.channel.send('An error occurred');
            }
        }

        if (!jailchannel) {
            try {
                jailchannel = await message.guild.channels.create('jail', {
                    type: 'GUILD_TEXT',
                    permissionOverwrites: [{
                        id: message.guild.id,
                        deny: ['VIEW_CHANNEL'],
                    }]
                });
                jailchannel.setPosition(0);
            } catch {
                message.channel.send('An error occurred');
            }
        }

        jailchannel.permissionOverwrites.edit(jailrole, {
            VIEW_CHANNEL: true,
            SEND_MESSAGES: true
        });

        user.roles.set([jailrole]).then(() => {
            message.channel.send(`**${user.user.username}** has been jailed 👍`);
        }).catch((err) => {
            message.channel.send(`An error occurred`);
        });

        jailchannel.send(`${user}, you've been jailed, contact staff about your punishment 👍`);
    }
};
