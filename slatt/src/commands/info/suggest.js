const { MessageEmbed } = require('discord.js');
const Command = require('../Command.js');

module.exports = class SUGGESTRIN extends Command {
    constructor(client) {
        super(client, {
            name: 'suggest',
            aliases: ['suggestion'],
            usage: 'suggest [suggestion]',
            description: 'Send suggestions to slatt, and become notified when a suggestion is aproved\n<:anti:828540580136484884> **useless troll suggestions will result in a server and user blacklist** <:anti:828540580136484884>',
            type: client.types.INFO
        });
    }
    async run(message, args) {
        const ms = require("parse-ms");
        const suggestion = args.join(' ')
        if (!suggestion) return this.send_info(message, `Provide a suggestion\n<:anti:828540580136484884> **useless troll suggestions will result in a server and user blacklist** <:anti:828540580136484884>`)
        const daily = this.db.get(`SUGGESTION_${message.author.id}`)
        let timeout = 43200000;
        if (daily !== null && timeout - (Date.now() - daily) > 0) {
            let time = ms(timeout - (Date.now() - daily));
            return this.send_info(message, `Wait **${time.hours}** hours and **${time.minutes}** minutes before making another suggestion`)
        } else {
            const EMB = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
            .setColor(this.hex)
            .setDescription(`**${suggestion}**`)
            .addField(`Author`, `${message.author.tag} (${message.author.id})`, true)
            .addField(`Guild`, `${message.guild.name} (${message.guild.id})`, true)
            .addField(`Channel`, `${message.channel.name} (${message.channel.id})`, true)
            .setFooter(`${message.guild.id}`)
            .setTimestamp()
        
            message.client.channels.cache.get('875941486670266409').send({embeds: [EMB]})
            this.db.set(`SUGGESTION_${message.author.id}`, Date.now())
            return this.send_info(message, `Suggestion sent. Responses can take anytime between **minutes**, **hours**, or more.\n**If you sent something stupid expect a blacklist**`)
        }
    }
}