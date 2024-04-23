const { Permissions, MessageEmbed, MessageAttachment } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'role',
        aliases: ['r'],
        description: 'Manage server roles',
        subcommands: ['> role humans\n> role bots\n> role create\n> role color\n> role delete'],
        syntax: 'role [subcommand] (args)',
        example: 'role @x6l gang',
        permissions: 'manage_roles',
        parameters: 'user, role',
        module: 'moderation'
    },
    run: async (session, message, args) => {

        const roleMention = message.content.match(/<@&(\d+)>/);
        const roleId = roleMention ? roleMention[1] : null;
        const roleName = args.slice(1).join(' ');
        const role = message.guild.roles.cache.get(roleId) || message.guild.roles.cache.find(r => r.name.toLowerCase() === roleName.toLowerCase());

        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                    .setColor(session.warn)
            ]
        });
        if (args.length < 2) {
            return displayCommandInfo(module.exports, session, message); 
        }

        const subcommand = args[0].toLowerCase();
        const roleColor = args[1];
        switch (subcommand) {
            case 'icon':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                const roleIconArg = args[1];
                let roleIconUrl = '';
                if (roleIconArg.toLowerCase() === 'none') {
                    roleIconUrl = null;
                } else {
                    const roleIcon = message.attachments.first();
                    if (!roleIcon) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.color)
                                    .setTitle('Command: role icon')
                                    .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                    .setDescription('Change the icon of a role\n```Syntax: role icon <role> (image)\nExample: role icon @gang [attachment]```')
                            ]
                        });
                    }
                    roleIconUrl = roleIcon.url;
                }

                try {
                    if (message.member.roles.highest.comparePositionTo(role) <= 0) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.warn)
                                    .setDescription(`${session.mark} ${message.author}: You cannot manage a role higher than yours`)
                            ]
                        });
                    }
                    await role.setIcon(roleIconUrl);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: Changed the icon of **${role.name}** to [this image](${roleIconUrl ? `[attachment](${roleIconUrl})` : 'none'}**`)
                        ]
                    });
                } catch (error) {
                    console.error('Error changing role icon:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: An error occurred while changing the role icon`)
                        ]
                    });
                }
            case 'humans':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                if (!role) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.color)
                                .setTitle('Command: role humans')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Assign a role to all humans\n```Syntax: role humans <role>\nExample: role humans @gang```')
                        ]
                    });
                }

                const humanMembers = message.guild.members.cache.filter(member => !member.user.bot);

                try {
                    for (const member of humanMembers.values()) {
                        if (message.member.roles.highest.comparePositionTo(role) > 0) {
                            await member.roles.add(role);
                        }
                    }
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: **${role.name}** has been granted to all humans`)
                        ]
                    });
                } catch (error) {
                    console.error('Error assigning role to humans:', error);
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.error)
                            .setDescription(`${session.mark} ${message.author}: An error occured while giving that role to humans`)
                    ]});
                }

            case 'delete':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                const deleteRole = message.mentions.roles.first();

                if (!deleteRole) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.color)
                                .setTitle('Command: role delete')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Delete a role\n```Syntax: role delete <role>\nExample: role delete @gang```')
                        ]
                    });
                }

                try {
                    await deleteRole.delete();
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: **${deleteRole.name}** has been deleted`)
                        ]
                    });
                } catch (error) {
                    console.error('Error deleting role:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: An error occurred while deleting the role`)
                        ]
                    });
                }

            case 'bots':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                const roleNameBots = args.join(' ');
                const botMembers = message.guild.members.cache.filter(member => member.user.bot);

                try {
                    const role = message.guild.roles.cache.find(r => r.name === roleNameBots);

                    if (!role) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.color)
                                    .setTitle('Command: role bots')
                                    .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                    .setDescription('Assign a role to all bots\n```Syntax: role bots <role>\nExample: role bots @bots```')
                            ]
                        });
                    }

                    for (const member of botMembers.values()) {
                        if (message.member.roles.highest.comparePositionTo(role) > 0) {
                            await member.roles.add(role);
                        }
                    }

                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: **${roleNameBots}** has been granted to all bots`)
                        ]
                    });
                } catch (error) {
                    console.error('Error assigning role to bots:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: An error occurred while assigning the role to bots`)
                        ]
                    });
                }
            case 'hoist':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                const hoistRole = message.mentions.roles.first();
                if (!hoistRole) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.color)
                                .setTitle('Command: role hoist')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Display a role above others\n```Syntax: role hoist <role>\nExample: role hoist @gang```')
                        ]
                    });
                }
                if (message.member.roles.highest.comparePositionTo(hoistRole) <= 0) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: You cannot manage a role higher than yours`)
                        ]
                    });
                }
                try {
                    await hoistRole.setHoist(true);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: **${hoistRole.name}** is now displayed above others`)
                        ]
                    });
                } catch (error) {
                    console.error('Error hoisting role:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: An error occurred while hoisting the role`)
                        ]
                    });
                }

            case 'create':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });
                try {
                    const role = await message.guild.roles.create({
                        name: roleName,
                        color: 'DEFAULT',
                    });
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: Created the role **${roleName}**`)
                        ]
                    });
                } catch (error) {
                    console.error('Error creating role:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.error)
                                .setDescription('An error occurred while creating the role.')
                        ]
                    });
                }
            case 'color':
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });

                try {
                    const role = message.mentions.roles.first() || message.guild.roles.cache.find(r => r.name === roleName);
                    const roleColor = args[1];

                    if (!role) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                .setColor(session.color)
                                .setTitle('Command: role icon')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Change the color of a role\n```Syntax: role color <role> (color)\nExample: role color @gang #ff0000```')
                            ]
                        });
                    }
                    if (!roleColor || !/^#[0-9A-F]{6}$/i.test(roleColor)) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.color)
                                    .setTitle('Command: role icon')
                                    .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                    .setDescription('Change the color of a role\n```Syntax: role color <role> (color)\nExample: role color @gang #ff0000```')
                            ]
                        });
                    }

                    await role.setColor(roleColor);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: Set the color of **${role.name}** to **${roleColor}**`)
                        ]
                    });
                } catch (error) {
                    console.error('Error changing role color:', error);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.error)
                                .setDescription('An error occurred while changing the role color.')
                        ]
                    });
                }

            default:
                if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                            .setColor(session.warn)
                    ]
                });
                const targetMember = message.mentions.members.first();
                if (!targetMember) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                            .setColor(session.color)
                            .setTitle('Command: role')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('Manage a user\'s roles```Syntax: role <user> (role)\nExample: role @x6l @gang```')
                        ]
                    });
                }
                if (!role) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.color)
                                .setTitle('Command: role')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Manage a user\'s roles```Syntax: role <user> (role)\nExample: role @x6l @gang```')
                        ]
                    });
                }
                if (message.member.roles.highest.comparePositionTo(role) <= 0) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: You cannot manage a role higher than yours`)
                        ]
                    });
                }
                try {
                    await targetMember.roles.add(role);
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: ${roleName} has been assigned to ${targetMember}`)
                        ]
                    });
                } catch (error) {
                    console.error('Error assigning role:', error);
                    return message.channel.send('An error occurred while assigning the role.');
                }
        }
    }
};
