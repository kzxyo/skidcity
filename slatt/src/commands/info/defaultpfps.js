const Command = require('../Command.js');

module.exports = class ServersCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'defaultpfps',
            aliases: ['nopfps'],
            description: `Sends the amount of users with discord default pfps, idk why i made this`,
            subcommands: [`defaultpfps`],
            type: client.types.INFO,
            usage: `defaultpfps`,
        });
    }
    async run(message) {
        let list = message.guild.members.cache.filter(u => u.user.displayAvatarURL({
            dynamic: true
        }).includes('https://cdn.discordapp.com/embed/avatars/')).map(u => u.user.displayAvatarURL({
            dynamic: true
        }))
       return this.send_info(message, `There are **${list.length}** users with default pfps here`)
    }
};