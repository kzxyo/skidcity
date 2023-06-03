const Subcommand = require('../../Subcommand.js');
const Discord = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js');

module.exports = class webhook_list extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'webhook',
            name: 'list',
            aliases: ['ls'],
            type: client.types.SERVER,
            usage: 'webhook list',
            clientPermissions: ['MANAGE_WEBHOOKS'],
            userPermissions: ['MANAGE_WEBHOOKS'],
            description: '<:anti:828540580136484884> do NOT run this command publicly. Webhook URLS may be leaked.',
        });
    }
    async run(message, args) {
        if (!message.guild.emojis.cache.size) {
            return this.send_error(message, 1, `There are no webhooks in this server`)
        }
        const row = new Discord.MessageActionRow()
            .addComponents(
                new Discord.MessageButton()
                    .setLabel(`Continue`)
                    .setStyle(`SUCCESS`)
                    .setCustomId('CONTINUE')
            )
            .addComponents(
                new Discord.MessageButton()
                    .setLabel(`Stop`)
                    .setStyle(`DANGER`)
                    .setCustomId('STOP')
            )
        const warn = new Discord.MessageEmbed()
            .setDescription(`${message.client.emotes.anti} ${message.author} Webhook URL's will be displayed, Are you sure you want to run this command here?`)
            .setColor("ffb636");
        const msg = await message.channel.send({ embeds: [warn], components: [row] })
        const filter = i => !i.isCommand() && i.isButton()
        const collector = msg.createMessageComponentCollector({ filter, time: 120000 });
        collector.on('collect', async reaction => {
            if (reaction.user.id != message.author.id) return reaction.reply({ content: `This button was not made for you.`, ephemeral: true })
            if (reaction.customId === 'CONTINUE') {
                collector.stop()
                const webhooks = await message.guild.fetchWebhooks()
                let num = 0
                let list = webhooks.map(e => `\`${++num}\` [**${e.name}**](${e.url})`)
                const embed = new Discord.MessageEmbed()
                    .setThumbnail(message.guild.iconURL({
                        dynamic: true
                    }))
                    .setDescription(list.join('\n'))
                    .setTitle(`Webhooks`)
                    .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                    .setColor(this.hex)
                    .setFooter(`${list.length} webhooks`)
                if (list.length <= 10) {
                    message.channel.send({ embeds: [embed] });
                } else {
                    new ReactionMenu(message.client, message.channel, message.member, embed, list);
                }
            } else {
                collector.stop()
            }
        });
        collector.on('end', () => {
            const end = new Discord.MessageEmbed()
                .setDescription(`<:info:828536926603837441> ${message.author} Prompt menu closed.`)
                .setColor("#78c6fe");
            msg.edit({ embeds: [end], components: [] }).then(msg => {
                setTimeout(function () {
                    msg.delete()
                }, 2000)
            })
        });

    }
}