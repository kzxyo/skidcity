const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')

module.exports = class Add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'wordfilter',
            name: 'remove',
            aliases: ['delete', 'destroy'],
            type: client.types.SERVER,
            usage: 'wordfilter remove [word] ',
            description: 'remove a filter from your filter settings',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const check = db.get(`word_filter_${message.guild.id}`)
        if(!check || !check.length) {
           return this.send_error(message, 1, `There arent any **word filters** to remove`)
        } 
        const word = args.join(' ').toLowerCase()
        if(!check.find(x => x === word)) return this.send_error(message, 1, `The word '${word}' is not filtered`)
        const arr = check.filter(x => x !== word)
        db.set(`word_filter_${message.guild.id}`, arr)
        //
        const check1 = db.get(`word_filter_${message.guild.id}_punish`)
        const arr1 = check1.filter(x => x.split(' --')[0] !== word)
        db.set(`word_filter_${message.guild.id}_punish`, arr1)
        return this.send_success(message, `Removed '${word}' from filter`)
        
    }
}