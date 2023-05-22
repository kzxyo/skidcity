const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js');

module.exports = class purge_embeds extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'purge',
            name: 'links',
            aliases: ['link'],
            type: client.types.MOD,
            usage: 'purge links',
            description: 'Purge links within the last 100 messages',
        });
    }
    async run(message, args) {
        message.delete()
        const messages = (await message.channel.messages.fetch({
            limit: 100
        })).filter(m => m.content.includes('http') || m.content.includes('.gg/') || m.content.includes('www'))
        if (messages.size === 0) {
            return this.send_error(message, 1, `There were no messages containing **links** in the last **100** messages`)
        } else {
            message.channel.bulkDelete(messages, true)
            message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `Links purged in ${message.channel}`)
            const embed = new MessageEmbed()
                .setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` Purged **${messages.size}** messages containing **links**`)
                .setColor("#007f00");
            message.channel.send({ embeds: [embed] }).then(msg => {setTimeout(function(){ msg.delete() }, 3000);})
        }
    }
}