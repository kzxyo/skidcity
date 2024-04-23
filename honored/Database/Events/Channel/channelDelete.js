const fs = require('fs');

module.exports = {
    configuration: {
        eventName: 'channelDelete',
        devOnly: false
    },
    run: async (session, channel) => {
        try {
            const configFilePath = `/root/rewrite/Database/Ticket/config.json`;
            let config = {};

            try {
                config = JSON.parse(fs.readFileSync(configFilePath, 'utf8'));
            } catch (error) {
            }

            const channelID = channel.id;
            if (config[channelID]) {
                delete config[channelID];
                fs.writeFileSync(configFilePath, JSON.stringify(config, null, 2), 'utf8');
            }
        } catch (error) {
        }
    }
};
