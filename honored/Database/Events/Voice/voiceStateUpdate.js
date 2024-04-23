const fs = require('fs');
const path = require('path');

const voicemasterDataPath = '/root/rewrite/Database/Settings/voicemaster.json';
const voiceConfigPath = '/root/rewrite/Database/Users/voicemaster.json';

module.exports = {
    configuration: {
        eventName: 'voiceStateUpdate',
        devOnly: false
    },
    run: async (session, oldState, newState) => {
        const guildID = newState.guild.id;

        if (fs.existsSync(voicemasterDataPath)) {
            const rawData = fs.readFileSync(voicemasterDataPath);
            const voicemasterData = JSON.parse(rawData);

            if (voicemasterData[guildID]) {
                const { categoryID, channelID, customName } = voicemasterData[guildID];
                const user = newState.member;

                let channelName = customName ? (customName === '{user}' ? user.user.username : customName) : `${user.user.username}'s voice call`;
                // Check if the custom name contains '{user}' and replace it with the channel creator's username
                channelName = channelName.replace(/\{user\}/g, user.user.username);

                if (newState.channelId === channelID) {
                    const userVoiceChannel = await newState.guild.channels.create(channelName, {
                        type: 'GUILD_VOICE',
                        parent: categoryID
                    });
                    await user.voice.setChannel(userVoiceChannel.id);
                    const intervalID = setInterval(() => {
                        if (userVoiceChannel.members.size === 0) {
                            userVoiceChannel.delete();
                            clearInterval(intervalID);

                            removeVoiceConfigEntry(user.id);
                        } else {
                            updateVoiceConfigEntry(user.id, userVoiceChannel.id);
                        }
                    }, 1000);
                }
            }
        }

        function updateVoiceConfigEntry(userID, voiceChannelID) {
            try {
                let voiceConfigData = {};
                if (fs.existsSync(voiceConfigPath)) {
                    const rawData = fs.readFileSync(voiceConfigPath);
                    voiceConfigData = JSON.parse(rawData);
                }
                voiceConfigData[userID] = voiceChannelID;
                fs.writeFileSync(voiceConfigPath, JSON.stringify(voiceConfigData, null, 4));
            } catch (error) {
                console.error('Error updating voice config:', error);
            }
        }

        function removeVoiceConfigEntry(userID) {
            try {
                if (fs.existsSync(voiceConfigPath)) {
                    const rawData = fs.readFileSync(voiceConfigPath);
                    let voiceConfigData = JSON.parse(rawData);
                    delete voiceConfigData[userID];
                    fs.writeFileSync(voiceConfigPath, JSON.stringify(voiceConfigData, null, 4));
                }
            } catch (error) {
                console.error('Error removing voice config entry:', error);
            }
        }
    }
};
