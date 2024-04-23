
const { MessageEmbed, MessageButton, MessageActionRow, Permissions } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const ticketsFilePath = '/root/rewrite/Database/Ticket/tickets.json';
const ticketsConfigFilePath = '/root/rewrite/Database/Ticket/config.json';
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'ticket',
        aliases: ['none'],
        description: 'Set up ticketing system in a specific channel.',
        usage: 'ticket channel #tickets',
        module: 'servers',
        subcommands: ['> ticket add\n> ticket remove\n> ticket channel\n> ticket category\n> ticket clear\n> ticket close']
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_GUILD')) {

            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                ]
            });
        }
        const subcommand = args[0];

        switch (subcommand) {
            case 'add': {
                const mentionedMember = message.mentions.members.first();
                const targetUser = mentionedMember || args[1];

                if (!targetUser) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Please specify a user to add to the ticket.`)
                        ]
                    });
                }

                const ticketData = loadTicketData(message.guild.id);

                if (!ticketData || !ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket category not set, hence why I cannot add a user to the ticket`)
                        ]
                    });
                }

                const ticketChannel = message.channel;

                if (ticketChannel.parentId !== ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: This channel is not a ticket channel`)
                        ]
                    });
                }

                ticketChannel.permissionOverwrites.edit(targetUser, {
                    VIEW_CHANNEL: true,
                    SEND_MESSAGES: true
                }).then(() => {
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: User has been added to the ticket successfully`)
                        ]
                    });
                }).catch(error => {
                    console.error('Error adding user to the ticket:', error);
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setDescription(`${message.author}: An error occurred while adding the user to the ticket`)
                        ]
                    });
                });
                break;
            }

            case 'name': {
                const customName = args.slice(1).join(' ');
            
                if (!customName) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Please specify a custom name for the ticket.`)
                        ]
                    });
                }
            
                const ticketData = loadTicketData(message.guild.id);
                ticketData.name = customName;
            
                saveTicketData(message.guild.id, ticketData);
            
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.green)
                            .setDescription(`${session.grant} ${message.author}: Custom name set to **${customName}**`)
                    ]
                });
                break;
            }

            case 'remove': {
                const mentionedMember = message.mentions.members.first();
                const targetUser = mentionedMember || args[1];

                if (!targetUser) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Please specify a user to remove from the ticket.`)
                        ]
                    });
                }

                const ticketData = loadTicketData(message.guild.id);

                if (!ticketData || !ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket category not set, hence why I cannot remove a user from the ticket`)
                        ]
                    });
                }

                const ticketChannel = message.channel;

                if (!ticketChannel || ticketChannel.parentId !== ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: This channel is not a ticket channel`)
                        ]
                    });
                }

                ticketChannel.permissionOverwrites.edit(targetUser, {
                    VIEW_CHANNEL: false,
                    SEND_MESSAGES: false
                }).then(() => {
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: User has been removed from the ticket successfully`)
                        ]
                    });
                }).catch(error => {
                    console.error('Error removing user from the ticket:', error);
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setDescription(`${message.author}: An error occurred while removing the user from the ticket`)
                        ]
                    });
                });
                break;
            }

            case 'blacklist': {
                const mentionedRoles = message.mentions.roles;
                const mentionedRole = mentionedRoles ? mentionedRoles.first() : null;
                const roleID = mentionedRole ? mentionedRole.id : args[1];

                if (!roleID) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Please specify a role to blacklist.`)
                        ]
                    });
                }

                const ticketData = loadTicketData(message.guild.id);

                if (!ticketData || !ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket category not set, hence why I cannot blacklist a role`)
                        ]
                    });
                }

                if (!ticketData.blacklistedRoles) {
                    ticketData.blacklistedRoles = [];
                }

                if (ticketData.blacklistedRoles.includes(roleID)) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Role is already blacklisted.`)
                        ]
                    });
                }

                ticketData.blacklistedRoles.push(roleID);

                saveTicketData(message.guild.id, ticketData);

                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.green)
                            .setDescription(`${session.grant} ${message.author}: Role has been blacklisted successfully.`)
                    ]
                });
                break;
            }

            case 'channel': {
                const ticketData = loadTicketData(message.guild.id);
                const channel = message.mentions.channels.first();

                if (!ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket category not set, please set a category first`)
                        ]
                    });
                }

                if (ticketData.channel) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket channel already set to <#${ticketData.channel}>`)
                        ]
                    });
                }

                if (!channel) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setTitle('Command: ticket channel')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Set a channel for ticket creation\n```Syntax: ticket channel <#channel>\nExample: ticket channel #tickets```')
                        ]
                    });
                }

                ticketData.channel = channel.id;

                const embed = new MessageEmbed()
                    .setAuthor(message.guild.name, message.guild.iconURL({ format: 'png', size: 512, dynamic: true }))
                    .setTitle('Create a ticket')
                    .setColor(session.color)
                    .setDescription(`Click on the button below this message to create a ticket`);

                const createButton = new MessageButton()
                    .setCustomId('create_ticket')
                    .setLabel('Create')
                    .setEmoji('🎫')
                    .setStyle('SECONDARY');

                const row = new MessageActionRow().addComponents(createButton);

                channel.send({ embeds: [embed], components: [row] }).then(sentMessage => {
                    ticketData.messageLink = sentMessage.url;
                    saveTicketData(message.guild.id, ticketData);
                });
                break;
            }
            case 'category': {
                const categoryID = args[1];
                const ticketData = loadTicketData(message.guild.id);

                if (!categoryID) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setTitle('Command: ticket category')
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setDescription('Set a category for ticket creation\n```Syntax: ticket category <category ID>\nExample: ticket category 1234567890```')
                        ]
                    });
                }

                ticketData.category = categoryID;

                saveTicketData(message.guild.id, ticketData);

                const embed = new MessageEmbed()
                    .setColor(session.green)
                    .setDescription(`${session.grant} ${message.author}: Ticket category set to **${categoryID}**`);

                message.channel.send({ embeds: [embed] });
                break;
            }
            case 'clear': {
                const ticketData = {
                    channel: null,
                    category: null,
                    messageLink: null
                };

                saveTicketData(message.guild.id, ticketData);

                const embed = new MessageEmbed()
                    .setColor(session.green)
                    .setDescription(`${session.grant} ${message.author}: Ticket configuration reset`);

                message.channel.send({ embeds: [embed] });
                break;
            }
            case 'close': {
                const ticketData = loadTicketData(message.guild.id);
                if (!ticketData || !ticketData.category) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Ticket category not set, hence why I cannot close the ticket`)
                        ]
                    });
                }

                const channelID = message.channel.id;
                const userID = ticketData[channelID];

                if (message.channel.parentId === ticketData.category) {
                    message.channel.delete()
                        .then(() => {
                            clearTicketSettings(message);
                            removeTicketConfig(message.guild.id, channelID, userID, ticketsConfigFilePath);
                        })
                        .catch(error => {
                            console.error('Error deleting ticket channel:', error);
                            message.channel.send({
                                embeds: [
                                    new MessageEmbed()
                                        .setDescription(`${message.author}: An error occurred while closing the ticket`)
                                ]
                            });
                        });
                } else {
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: This channel is not a ticket channel`)
                        ]
                    });
                }
                break;

            }
            default:
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setTitle('Command: ticket')
                            .setDescription('Set up tickets for your server```Syntax: ticket [subcommands] (args)\nExample: ticket channel #tickets```')
                            .setColor(session.color)
                            .addField('Subcommands:', '`ticket add` - add a user to the ticket\n`ticket remove` - remove a user from the ticket\n`ticket channel` - set the ticket channel\n`ticket category` - set the ticket category\n`ticket clear` - reset ticket settings\n`ticket close` - close the ticket channel')
                    ]
                });
                break;
        }
    }
};

function clearTicketSettings(guildID) {
    try {
        const ticketData = loadTicketData(guildID);
        ticketData.channel = null;
        ticketData.category = null;
        ticketData.messageLink = null;
        saveTicketData(guildID, ticketData);
    } catch (error) {
        console.error('Error clearing ticket settings:', error);
    }
}

function removeTicketConfig(guildID, channelID, userID, configFilePath) {
    try {
        let config = JSON.parse(fs.readFileSync(configFilePath, 'utf8'));
        delete config[channelID];
        fs.writeFileSync(configFilePath, JSON.stringify(config, null, 2), 'utf8');
    } catch (error) {
        console.error('Error removing ticket config:', error);
    }
}


function saveTicketData(guildID, ticketData, session) {
    try {
        let ticketConfig = JSON.parse(fs.readFileSync(ticketsFilePath, 'utf8'));
        ticketConfig[guildID] = ticketData;
        fs.writeFileSync(ticketsFilePath, JSON.stringify(ticketConfig, null, 2), 'utf8');
    } catch (error) {
        console.error('Error saving ticket data:', error);
    }
}

function loadTicketData(guildID) {
    try {
        const rawData = fs.readFileSync(ticketsFilePath, 'utf8');
        const ticketData = JSON.parse(rawData);
        return ticketData[guildID] || { channel: null, category: null, messageLink: null };
    } catch (error) {
        console.error('Error loading ticket data:', error);
        return { channel: null, category: null, messageLink: null };
    }
}
