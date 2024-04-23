const fs = require('fs');
const path = require('path');
const { MessageEmbed } = require('discord.js');

// Database
const guildDataFilePath = '/root/rewrite/Database/Settings/tracker.json';
const vanitytrackerPath = '/root/lain/lain/Database/config/vanitytracker.json';

module.exports = {
    configuration: {
        eventName: 'guildUpdate',
        devOnly: false
    },
    run: async (session, oldGuild, newGuild) => {
        try {
            let guildData = {};
            if (fs.existsSync(guildDataFilePath)) {
                guildData = JSON.parse(fs.readFileSync(guildDataFilePath, 'utf8'));
            }

            if (!guildData[newGuild.id]) {
                guildData[newGuild.id] = {};
            }

            if (oldGuild.name !== newGuild.name) {
                guildData[newGuild.id].names = guildData[newGuild.id].names || [];
                guildData[newGuild.id].names.push(oldGuild.name);
                guildData[newGuild.id].name = newGuild.name;
            }

            fs.writeFileSync(guildDataFilePath, JSON.stringify(guildData, null, 4));

            const vanityTrackerData = JSON.parse(fs.readFileSync(vanitytrackerPath, 'utf-8'));
            const oldVanityURL = oldGuild.vanityURLCode;
            const newVanityURL = newGuild.vanityURLCode;
            if (oldVanityURL !== newVanityURL) {
                for (const guildId in vanityTrackerData) {
                    const channelId = vanityTrackerData[guildId];
                    const guild = session.guilds.cache.get(guildId);
                    if (guild) {
                        const channel = guild.channels.cache.get(channelId);
                        if (channel && channel.isText()) {
                            channel.send({ embeds: [
                                new MessageEmbed()
                                    .setDescription(`> The vanity **${oldVanityURL}** is now available`)
                                    .setColor(session.info)
                            ] });
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error handling guild update:', error);
        }
    }
};
