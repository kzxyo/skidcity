const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js');

module.exports = class purge_word extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'purge',
            name: 'word',
            aliases: ['match', 'string', 'contains', 'contain'],
            type: client.types.MOD,
            usage: 'purge word [some_word]',
            description: 'Purge all messages containing a certain string',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        message.delete()
        const word = args.join(' ')
        const messages = (await message.channel.messages.fetch({
            limit: 100
        })).filter(m => m.content.includes(word))
        if(messages.size === 0) {
            return this.send_error(message, 1, `There were no messages containing '${word}' in the last **100** messages`)
        } else {
            message.channel.bulkDelete(messages, true)
            message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `String: '${word}' purged in ${message.channel}`)
            const embed = new MessageEmbed()
                .setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Purged **${messages.size}** messages containing '${word}'`)
                .setColor("#007f00");
            message.channel.send({ embeds: [embed] }).then(msg => {setTimeout(function(){ msg.delete() }, 3000);})
        }
    }
}