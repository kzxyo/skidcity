const Command = require('../Command.js');

module.exports = class EncodeCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'encode',
            aliases: ['base64', 'b64'],
            usage: 'encode [txt',
            subcommands: ['encode'],
            description: 'Encode a text into base64',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const b64Encoded = Buffer.from(args.join(" ")).toString("base64");
        return this.send_info(message, `Heres your Base64 string: \`${b64Encoded}\``)
    }
}