const Command = require('../Command.js');


module.exports = class SetavCommand extends Command {
    constructor(client) {
        super(client, {
            name: "setav",
            subcommands: [`setav`],
            aliases: ["setavatar"],
            usage: `setav [link]`,
            description: 'sets the avatar for Kami',
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }

    async run(message, [image]) {
        this.client.user.setAvatar(image);
        return this.send_success(message, "new avatar set ");
    }
};