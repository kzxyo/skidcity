const { MessageEmbed, Permissions } = require('discord.js');
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'fortnite',
        aliases: ['fort', 'fn'],
        description: 'Fortnite cosmetic-related commands',
        syntax: 'fortnite (subcommands) <args>',
        example: 'fortnite lookup Renegade Raider',
        permissions: 'N/A',
        parameters: 'subcommand',
        subcommands: ['> fortnite shop\n> fortnite lookup'],
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        const commands = ['lookup', 'search', 'find', 'shop', 'store', 'channel'];
        const command = args[0]?.toLowerCase();

        if (!command || !commands.includes(command)) {
            return displayCommandInfo(module.exports, session, message);
        }

        switch (command) {
            case 'lookup':
            case 'search':
            case 'find': {
                const cosmetic = args.slice(1).join(' ');
                if (!cosmetic) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.color)
                                .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                                .setTitle('Command: fortnite lookup')
                                .setDescription('Search for a cosmetic with occurrences\n```Syntax: fortnite lookup [cosmetic]\nExample: fortnite lookup Renegade Raider```')
                        ]
                    });
                }

                try {
                    const response = await axios.get(`https://fnbr.co/api/images?search=${encodeURIComponent(cosmetic)}`, {
                        headers: {
                            'x-api-key': 'ed183402-89c6-4ffa-a63a-bd462c4521d1'
                        }
                    });
                    const data = response.data;

                    if (data.status !== 200 || data.data.length === 0) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.warn)
                                    .setDescription(`${session.mark} ${message.author}: No cosmetic found with the name \`${cosmetic}\``)
                            ]
                        });
                    }

                    const { name, description, type, readableType, rarity, images, price } = data.data[0];
                    const embed = new MessageEmbed()
                        .setTitle(name)
                        .setURL(session.server)
                        .setDescription(description)
                        .addField('Type', `> ${readableType}`, true)
                        .addField('Rarity', `> ${rarity}`, true)
                        .setThumbnail(images.icon)
                        .setFooter(`${price} V-Bucks`, 'https://image.fnbr.co/price/icon_vbucks.png')
                        .setColor(session.color)

                    message.channel.send({ embeds: [embed] });
                } catch (error) {
                    session.log('Error:', error.message);
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`An error occurred while searching for the cosmetic: ${error.message}`)
                        ]
                    });
                }

                break;
            }
            case 'shop':
            case 'store': {
                try {
                    const date = new Date();
                    const format = `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
                    const shopImageUrl = `https://bot.fnbr.co/shop-image/fnbr-shop-${format}.png`;

                    const embed = new MessageEmbed()
                        .setTitle('Fortnite Item Shop')
                        .setImage(shopImageUrl)
                        .setColor(session.color);

                    message.channel.send({ embeds: [embed] });
                } catch (error) {
                    session.log('Error:', error.message);
                    message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`An error occurred while getting the Fortnite item shop: ${error.message}`)
                        ]
                    });
                }
            }
                break;

            default:
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: API returned an errorr`)
                    ]
                });
        }
    }
}
