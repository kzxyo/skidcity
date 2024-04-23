const fs = require('fs');
const { MessageEmbed, Permissions } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const trackerPath = '/root/rewrite/Database/Settings/vanities.json';

module.exports = {
    configuration: {
        commandName: 'vanityset',
        aliases: ['vanity'],
        description: 'Log available vanities in a channel',
        syntax: 'vanityset <subcommands> (args)',
        example: 'vanityset set #vanity',
        permissions: 'manage_guild',
        parameters: 'channel',
        module: 'servers'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_GUILD')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                        .setColor(session.warn)
                ]
            });
        }

        if (args[0] === 'set') {
            const channelID = message.mentions.channels.first()?.id || args[1];
            const channel = message.guild.channels.cache.get(channelID);

            if (!channel || channel.type !== 'GUILD_TEXT') {
                return displayCommandInfo(module.exports, session, message);
            }

            let trackerData = {};

            if (fs.existsSync(trackerPath)) {
                const rawData = fs.readFileSync(trackerPath);
                trackerData = JSON.parse(rawData);
            }

            trackerData[message.guild.id] = channelID;

            fs.writeFileSync(trackerPath, JSON.stringify(trackerData, null, 2));

            const embedSet = new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: Logging available vanities in **\#${channel.name}**`);

            return message.channel.send({ embeds: [embedSet] });
        } else if (args[0] === 'reset') {
            let trackerData = {};

            if (fs.existsSync(trackerPath)) {
                const rawData = fs.readFileSync(trackerPath);
                trackerData = JSON.parse(rawData);
            }

            delete trackerData[message.guild.id];

            fs.writeFileSync(trackerPath, JSON.stringify(trackerData, null, 2));

            const embedReset = new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: No longer tracking available vanities`);

            return message.channel.send({ embeds: [embedReset] });
        } else {
            return displayCommandInfo(module.exports, session, message);
        }
    }
};
