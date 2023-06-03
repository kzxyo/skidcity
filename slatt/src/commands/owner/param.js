const Command = require('../Command.js');
module.exports = class param extends Command {
    constructor(client) {
        super(client, {
            name: 'param'
        });
    }

    async run(message, args) {
           
    }
}