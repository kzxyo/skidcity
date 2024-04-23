const fs = require('fs');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        eventName: 'interactionCreate',
        devOnly: false
    },
    run: async (session, interaction) => {
        try {
            if (!interaction.isMessageComponent()) return;

            const guildID = interaction.guildId;
            const ticketsConfigFilePath = `/root/rewrite/Database/Ticket/tickets.json`;
            const configFilePath = `/root/rewrite/Database/Ticket/config.json`;

            let ticketsConfig = {};
            let config = {};

            try {
                ticketsConfig = JSON.parse(fs.readFileSync(ticketsConfigFilePath, 'utf8'));
                config = JSON.parse(fs.readFileSync(configFilePath, 'utf8'));
            } catch (error) {
                console.error('Error loading ticket configuration:', error);
            }

            const messageLink = interaction.message.url;
            const ticketData = Object.values(ticketsConfig).find(data => data.messageLink === messageLink);

            if (!ticketData) return;

            const userID = interaction.user.id;
            const existingTicketChannel = Object.keys(config).find(channelID => config[channelID] === userID);

            if (existingTicketChannel) {
                interaction.reply({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${interaction.user}: You already have a ticket open`)
                    ],
                    ephemeral: true
                });
                return;
            }

            // Check if the user has the blacklisted role
            const blacklistRoleID = ''; // Replace with the ID of your blacklisted role
            const member = await interaction.guild.members.fetch(userID);
            if (member.roles.cache.has(blacklistRoleID)) {
                interaction.reply({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${interaction.user}: You are not allowed to create a ticket.`)
                    ],
                    ephemeral: true
                });
                return;
            }

            let channelName = ticketData.name || '{user}s-ticket';

            // Replace {user} with the interaction user's username
            if (channelName.includes('{user}')) {
                channelName = channelName.replace('{user}', interaction.user.username);
            }

            // Check if the category ID is available
            if (!ticketData.category) {
                console.error('Parent category ID not found.');
                interaction.reply({
                    content: 'Error: Parent category not found. Please contact the server administrator.',
                    ephemeral: true
                });
                return;
            }

            const ticketChannel = await interaction.guild.channels.create(channelName, {
                type: 'text',
                parent: ticketData.category, // Assign the category ID here
                permissionOverwrites: [
                    {
                        id: interaction.guild.roles.everyone,
                        deny: ['VIEW_CHANNEL']
                    },
                    {
                        id: interaction.user.id,
                        allow: ['VIEW_CHANNEL', 'SEND_MESSAGES']
                    }
                ]
            });

            const channelID = ticketChannel.id;
            ticketChannel.send({
                content: `${interaction.user}`,
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setTitle('Ticket created')
                        .setDescription(`Please wait for staff to the answer the ticket`)
                ]
            });

            config[channelID] = interaction.user.id;
            fs.writeFileSync(configFilePath, JSON.stringify(config, null, 4));

            interaction.reply({
                content: `Ticket channel ${ticketChannel} created successfully.`,
                ephemeral: true
            });
        } catch (error) {
            console.error('Error handling interaction:', error);
            interaction.reply({
                content: 'An error occurred while processing your request.',
                ephemeral: true
            });
        }
    }
};
