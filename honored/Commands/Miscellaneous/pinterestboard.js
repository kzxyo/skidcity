const { MessageActionRow, MessageButton, MessageEmbed, MessageAttachment } = require('discord.js');
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: "pinterestboard",
        aliases: ['pint'],
        description: "Search pins or view a user's pins on Pinterest",
        syntax: "pinterest add [channel] (username)",
        example: "pinterest add #pfps hygric",
        subcommands: ['> pinterest add\n> pinterest search'],
        module: 'miscellaneous',
    },
    run: async (session, message, args) => {
        const subcommand = args[0]?.toLowerCase();

        if (subcommand === 'add') {
            if (!message.member.permissions.has('MANAGE_GUILD')) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: You are **missing** \`manage_server\` permissions`)
                            .setColor(session.warn)
                    ]
                });
            }

            const channelArg = args[1];
            const username = args[2];

            if (!channelArg || !username) {
                return displayCommandInfo(module.exports, session, message);
            }
            let channel;
            if (channelArg.startsWith('<#') && channelArg.endsWith('>')) {
                const channelId = channelArg.slice(2, -1);
                channel = message.guild.channels.cache.get(channelId);
            } else {
                const channelName = channelArg.replace(/^#/, '');
                channel = message.guild.channels.cache.find(ch => ch.name === channelName);
            }
            if (!channel) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: Channel not found`)
                            .setColor(session.warn)
                    ]
                });
            }
            try {
                const pins = await fetchPins(username);
                if (pins.length === 0) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setDescription(`${session.mark} ${message.author}: No pins found for the provided username`)
                                .setColor(session.warn)
                        ]
                    });
                }
                let attachments = [];
                let i = 0;
                for (const pin of pins) {
                    if (i >= 2) {
                        await channel.send({ files: attachments });
                        attachments = [];
                        i = 0;
                    }
                    const attachment = new MessageAttachment(pin.image);
                    attachments.push(attachment);
                    i++;
                }
                if (attachments.length > 0) {
                    await channel.send({ files: attachments });
                }
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: ${pins.length} pins sent to ${channel}`)
                            .setColor(session.green)
                    ]
                });
            } catch (error) {
                console.error('Error fetching or sending pins:', error);
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: The API returned an error`)
                            .setColor(session.warn)
                    ]
                });
            }
        } else {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                        .setTitle('Command: pinterest')
                        .setDescription('Search Pinterest\n```Syntax: pinterest add [channel] (username)\nExample: pinterest add #pfps hygric```')
                ]
            });
        }
    }
};

async function fetchPins(username) {
    const pinsUrl = `https://api.pinterest.com/v3/pidgets/users/${username}/pins/`;
    const response = await axios.get(pinsUrl);
    const pins = response.data.data.pins.map(pin => ({
        description: pin.description || 'Pin',
        url: `https://www.pinterest.com${pin.link}`,
        image: pin.images['564x'].url
    }));
    return pins;
}
