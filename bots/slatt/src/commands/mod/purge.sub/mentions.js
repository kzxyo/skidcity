const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js');

module.exports = class purge_mentions extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'purge',
            name: 'mentions',
            aliases: ['mention', 'pings'],
            type: client.types.MOD,
            usage: 'purge mentions',
            description: 'Purge mentions within the last 100 messages',
        });
    }
    async run(message, args) {
        const messages = (await message.channel.messages.fetch({
            limit: 100
        })).filter(m => m.mentions.members.first())
        if(messages.size === 0) {
            return this.send_error(message, 1, `There were no messages containing **mentions** in the last **100** messages`)
        } else {
            message.channel.bulkDelete(messages, true)
            message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `Mentions purged in ${message.channel}`)
            const embed = new MessageEmbed()
                .setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Purged **${messages.size}** messages containing **mentions**`)
                .setColor("#007f00");
            message.channel.send({ embeds: [embed] }).then(msg => {setTimeout(function(){ msg.delete() }, 3000);})
        }
    }
}