const { MessageEmbed } = require('discord.js');
const Command = require('../Command.js');

module.exports = class Akinator extends Command {
    constructor(client) {
        super(client, {
            name: 'snipe',
            aliases: ['s'],
            usage: 'snipe',
            description: 'Snipe deleted messages',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        let embed = new MessageEmbed()
        const snipes = this.db.get(`Snipes_${message.guild.id}`)
        if (snipes) {
            if (snipes.embed) {
                embed = embed = new MessageEmbed(snipes.embed)
                embed.setAuthor(snipes.author.tag, snipes.author.displayAvatarURL)
                .setFooter(`Sniped by ${message.author.tag}`)
                .setColor(this.hex)
                .setTimestamp(snipes.time)
                if(!snipes.embed.description) embed.setDescription(snipes.message.content)
            } else if(snipes.attachments) {
                embed.setAuthor(snipes.author.tag, snipes.author.displayAvatarURL)
                .setDescription(snipes.message.content)
                .addField(`Attachment:`, `[${snipes.attachments.name}](${snipes.attachments.url})`)
                .setImage(snipes.attachments.url)
                .setFooter(`Sniped by ${message.author.tag}`)
                .setColor(this.hex)
                .setTimestamp(snipes.time)
            } else {
                embed.setAuthor(snipes.author.tag, snipes.author.displayAvatarURL)
                .setDescription(`${snipes.message.content}`)
                .setFooter(`Sniped by ${message.author.tag}`)
                .setColor(this.hex)
                .setTimestamp(snipes.time)
            }
            return message.channel.send({ embeds: [embed] })

        } else {
            return this.send_error(message, 1, `There werent any **recently deleted** messages found`)
        }
    }
};