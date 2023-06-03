const Command = require('../Command.js');
const fetch = require('node-fetch');
const { MessageEmbed } = require('discord.js');

module.exports = class Joke extends Command {
    constructor(client) {
        super(client, {
            name: 'joke',
            aliases: ['funny'],
            usage: 'joke',
            description: 'return random jokes',
            type: client.types.FUN
        });
    }
    async run(message) {
        fetch('https://v2.jokeapi.dev/joke/Any').then(response => response.json()).then(res => {
            if (!res || !res.delivery || !res.setup) {
                return this.api_error(message, 'random joke')
            }
            const embed = new MessageEmbed()
                .setColor(this.hex)
                .addField(`Joke`, res.setup)
                .addField(`Punchline`, res.delivery)
                .setTitle(':joy:')
            message.channel.send({ embeds: [embed] })
        })
    }
};