const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')

module.exports = class Add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'wordfilter',
            name: 'add',
            aliases: ['create', 'new'],
            type: client.types.SERVER,
            usage: 'wordfilter add [word] ',
            description: 'Filter a new word',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const check = db.get(`word_filter_${message.guild.id}`)
        if(!check) {
            db.set(`word_filter_${message.guild.id}`, []); 
            db.set(`word_filter_${message.guild.id}_punish`, [])
        }
        let string
        let punishment
        if (args.join(' ').includes('--')) {
            let word = args.join(' ').split(' --')
            string = word[0].toLowerCase()
            if (word[1].toLowerCase() === 'ban' || word[1].toLowerCase() === 'kick' || word[1].toLowerCase() === 'mute' || word[1].toLowerCase() === 'delete') {
                punishment = word[1]
            } else {
                punishment = 'mute'
            } 
            db.push(`word_filter_${message.guild.id}`, string)
            db.push(`word_filter_${message.guild.id}_punish`, `${string} --${punishment}`)
            return this.send_success(message, `Added a filter for word: **${string}** with punishment: **${punishment}**`)
        } else {
            string = args.join(' ').toLowerCase()
            db.push(`word_filter_${message.guild.id}`, string)
            db.push(`word_filter_${message.guild.id}_punish`, `${string} --mute`)
            return this.send_success(message, `Added a filter for word: **${string}** with punishment: **mute**`)
        }
    }
}