const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const fetch = require('node-fetch');

module.exports = class kanye extends Command {
    constructor(client) {
        super(client, {
            name: 'kanye',
            aliases: ['kanyewest', 'kanyequote'],
            usage: 'kanye',
            description: 'A random quote that kanye once said',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        fetch('https://api.kanye.rest/?format=json')
            .then(response => response.json())
            .then(res => {
                if (!res) {
                    return this.api_error(message, `Kanye Quote`)
                }
                const embed = new MessageEmbed()
                    .setColor(this.hex)
                    .setAuthor('Kanye.', 'https://cdn.discordapp.com/attachments/832103367882309712/865529691632959488/https3A2F2Fspecials-images.png')
                    .setDescription(res.quote)
                message.channel.send({ embeds: [embed] });
            })
    }
};