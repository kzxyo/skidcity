const Subcommand = require('../../Subcommand.js');
const db = require('quick.db');
const { MessageEmbed } = require('discord.js');

module.exports = class Boostmessage extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'boost',
            name: 'config',
            aliases: ['settings'],
            type: client.types.SERVER,
            usage: 'boost config',
            description: 'View your servers boost settings',
        });
    }
    async run(message, args) {
        const msg = await message.client.db.boost_message.findOne({ where: { guildID: message.guild.id } })
        const channel = await message.client.db.boost_channel.findOne({ where: { guildID: message.guild.id }})
        const embed = new MessageEmbed()
            .setTitle(`Boost settings`)
            .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
            .setColor(this.hex)
            .addField(`Boost message`, msg !== null ? `${msg.message}` : 'No message')
            .addField(`Boost channel`, channel !== null ? `${message.guild.channels.cache.get(channel.channel)}` : 'No channel')
        message.channel.send({ embeds: [embed] })
    }
}