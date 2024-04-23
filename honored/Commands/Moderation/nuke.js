const { MessageActionRow, MessageButton, MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'nuke',
        aliases: ['recreate'],
        description: 'Deletes and recreates the current channel.',
        syntax: 'nuke',
        example: 'nuke',
        permissions: 'administrator',
        parameters: 'N/A',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has('ADMINISTRATOR')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** the \`administrator\` permission`)
                        .setColor(session.warn)
                ]
            });
        }

        const channel = message.channel;
        const channelName = channel.name;
        const channelPosition = channel.rawPosition;
        const channelParent = channel.parentId;

        const confirmationMessage = await message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: Are you sure you want to nuke this channel?`)
                    .setColor(session.warn)
            ],
            components: [
                new MessageActionRow()
                    .addComponents(
                        new MessageButton()
                            .setCustomId('confirm')
                            .setLabel('Yes')
                            .setStyle('SUCCESS'),
                        new MessageButton()
                            .setCustomId('cancel')
                            .setLabel('No')
                            .setStyle('DANGER')
                    )
            ]
        });

        const filter = i => i.user.id === message.author.id;
        const collector = confirmationMessage.createMessageComponentCollector({ filter, time: 15000 });

        collector.on('collect', async i => {
            if (i.customId === 'confirm') {
                try {
                    await channel.delete();

                    const recreatedChannel = await channel.clone();
                    await recreatedChannel.setPosition(channelPosition);
                    if (channelParent) {
                        await recreatedChannel.setParent(channelParent);
                    }

                    await recreatedChannel.send({ content: `first` });

                } catch (error) {
                    console.error('Error nuking channel:', error);
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setDescription(`${session.mark} ${message.author}: Error nuking channel`)
                                .setColor(session.warn)
                        ]
                    });
                }
            } else if (i.customId === 'cancel') {
                await confirmationMessage.delete();
            }
        });

        collector.on('end', collected => {
            if (collected.size === 0) {
                confirmationMessage.edit({ content: 'you took to long..', components: [] });
            }
        });
    }
};
