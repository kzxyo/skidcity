const Client = require('./src/Client.js');
const config = require('./src/utils/json/config.json')
const {
    Intents,
    DiscordAPIError,
} = require('discord.js');
global.__basedir = __dirname;
const client = new Client();
function init() {
    client.loadEvents('./src/events');
    client.loadCommands('./src/commands');
    client.login(config.token);
}




init();
process.on('unhandledRejection', err => {
    if (err instanceof DiscordAPIError) {
        client.logger.error(`${err} at ${err.path} (${err.code})`)
    } else {
        client.logger.error(err)
    }      
})

