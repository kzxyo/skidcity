const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const filePath = '/root/rewrite/Database/lastfm.json';

module.exports = {
    configuration: {
        commandName: 'lastfm',
        aliases: ['lf'],
        description: 'Interact with your music',
        syntax: 'lastfm set larplol',
        example: 'lastfm set larplol',
        module: 'lastfm',
        subcommands: ['> lastfm set\n> lastfm reset']
    },
    run: async (session, message, args) => {
        const key = session.lastfmkey;
        if (!args[0]) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor(session.color)
                    .setTitle('Command: lastfm')
                    .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                    .setDescription('Interact with your music\n```Syntax: lastfm [subcommand] (args)\nExample: lastfm set larplol```')
                    .addField('Subcommands:', '`lastfm set` - set your username\n`lastfm reset` - reset your username')
            ]
        });

        const subcommand = args.shift().toLowerCase();
        const userID = message.author.id;
        const lastfmData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        switch (subcommand) {
            case 'set':
                if (!args[0]) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor('#FF0000')
                            .setDescription(`<:lastfm:1210618435411775549> ${message.author}: You must provide your LastFM username. \`lastfm set [username]\``)
                    ]
                });

                if (lastfmData[userID]) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: You already have a LastFM username set`)
                    ]
                });

                try {
                    const { data } = await axios.get(`https://ws.audioscrobbler.com/2.0/?method=user.getInfo&user=${args[0]}&api_key=${session.lastfmkey}&format=json`);

                    if (data.error) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor('#FF0000')
                                    .setDescription(`<:lastfm:1210618435411775549> ${message.author}: The provided LastFM username is not valid.`)
                            ]
                        });
                    }

                    lastfmData[userID] = args[0];
                    fs.writeFileSync(filePath, JSON.stringify(lastfmData, null, 4));

                    return message.react('✅');
                } catch (error) {
                    console.error('Error setting LastFM username:', error);
                    return message.channel.send('An error occurred while setting LastFM username.');
                }

            case 'reset':
                if (!lastfmData[userID]) return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor('#FF0000')
                            .setDescription(`<:lastfm:1210618435411775549> ${message.author}: You don't have a LastFM username set! Run \`lastfm set [username]\``)
                    ]
                });
                delete lastfmData[userID];
                fs.writeFileSync(filePath, JSON.stringify(lastfmData, null, 4));
                return message.react('✅');

            default:
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.color)
                            .setTitle('Command: lastfm')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('Interact with your music\n```Syntax: lastfm [subcommand] (args)\nExample: lastfm set larplol```')
                            .addField('Subcommands:', '`lastfm set` - set your username\n`lastfm reset` - reset your username')
                    ]
                });
        }
    }
};
