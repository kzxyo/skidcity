const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const voicemasterSettingsPath = '/root/rewrite/Database/Settings/voicemaster.json';
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'voicemaster',
        aliases: ['vm'],
        description: 'Setup Voicemaster category and channels.',
        syntax: 'voicemaster <subcommands> (args)',
        example: 'voicemaster setup',
        permissions: 'manage_guild',
        parameters: 'N/A',
        module: 'servers',
        subcommands: ['> voicemaster setup\n> voicemaster remove\n> voicemaster setname']

    },
    run: async (session, message, args) => {
        const { member, guild } = message;
        const guildID = guild.id;
        let voicemasterData = {};

        if (!member.permissions.has('MANAGE_GUILD')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                ]
            });
        }

        if (fs.existsSync(voicemasterSettingsPath)) {
            const rawData = fs.readFileSync(voicemasterSettingsPath);
            voicemasterData = JSON.parse(rawData);
        }

        switch (args[0]) {
            case 'setup':
                if (voicemasterData[guildID]) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: Voicemaster is already set up for this server`)
                        ]
                    });
                }
                const voicemasterCategory = await guild.channels.create('Voicemaster', { type: 'GUILD_CATEGORY' });
                const joinToCreateChannel = await guild.channels.create('Join to create', { type: 'GUILD_VOICE', parent: voicemasterCategory.id });
                voicemasterData[guildID] = { categoryID: voicemasterCategory.id, channelID: joinToCreateChannel.id };
                fs.writeFileSync(voicemasterSettingsPath, JSON.stringify(voicemasterData, null, 2));
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.green)
                            .setDescription(`${session.grant} ${message.author}: Voicemaster has been set up for this server`)
                    ]
                });
            case 'remove':
                if (!voicemasterData[guildID]) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed().setColor(session.warn).setDescription(`${session.mark} ${message.author}: Voicemaster is not set up for this server. Use \`voicemaster setup\` first.`)
                        ]
                    });
                }
                const { categoryID, channelID } = voicemasterData[guildID];
                const categoryToDelete = guild.channels.cache.get(categoryID);
                const channelToDelete = guild.channels.cache.get(channelID);
                if (categoryToDelete) await categoryToDelete.delete();
                if (channelToDelete) await channelToDelete.delete();
                delete voicemasterData[guildID];
                fs.writeFileSync(voicemasterSettingsPath, JSON.stringify(voicemasterData, null, 2));
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.green)
                            .setDescription(`${session.grant} ${message.author}: Voicemaster has been removed from this server.`)
                    ]
                });
            case 'setname':
                if (!voicemasterData[guildID]) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: Voicemaster is not set up for this server. Use \`voicemaster setup\` first`)
                        ]
                    });
                }
                const givenName = args.slice(1).join(' ');
                if (!givenName) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                            .setColor(session.color)
                            .setAuthor(`${session.user.username} help`, `${session.user.displayAvatarURL({ dynamic: true })}`)
                            .setTitle('Command: voicemaster setname')
                            .setDescription('Set a custom voicemaster name for the voice channels```Syntax: voicemaster setname [name]\nExample: voicemaster setname {user}\'s channel```')
                        ]
                    });
                }
                voicemasterData[guildID].customName = givenName;
                fs.writeFileSync(voicemasterSettingsPath, JSON.stringify(voicemasterData, null, 2));
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.green)
                            .setDescription(`${session.grant} ${message.author}: I will now name the voice channels as **${givenName}**`)
                    ]
                });
            default:
                return displayCommandInfo(module.exports, session, message);
        }
    }
};
