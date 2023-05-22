const Command = require('../Command.js');
const fetch = require('node-fetch');
const { MessageEmbed } = require('discord.js');

module.exports = class Kiss extends Command {
    constructor(client) {
        super(client, {
            name: 'kiss',
            aliases: ['smooch', 'muah'],
            usage: 'kiss [member]',
            description: 'kiss people.',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const member = this.functions.get_member(message, args.join(' '))
        if (!member) return this.invalidUser(message)
        fetch('http://api.nekos.fun:8080/api/kiss').then(response => response.json()).then(res => {
            if (!res) {
                return this.api_error(message, 'random image')
            }
            const embed = new MessageEmbed()
                .setColor(this.hex)
                .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
                .setDescription(`**${message.member.nickname || message.member.user.username}** kisses **${member.nickname || member.user.username}**`)
                .setImage(res.image)
            message.channel.send({ embeds: [embed] })
        })
    }
};