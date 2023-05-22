const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const { stripIndent } = require('common-tags');

module.exports = class notify extends Command {
    constructor(client) {
        super(client, {
            name: 'notify',
            aliases: [`update`],
            usage: `notify [new update]`,
            description: 'Send updates',
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        const ReactionMenu = require('../ReactionMenu')
        if (!args.length) {
            const channels = (await message.client.db.updates.findAll()).filter(x => message.client.guilds.cache.get(x.guildID))
            let num = 0
            function info(guild) {
                return `**${guild.name}** (${guild.memberCount.toLocaleString()}) `
            }
            const list = channels.map(x => `\`${num++}\` ${info(message.client.guilds.cache.get(x.guildID))}`)
            const embed = new MessageEmbed()
            .setTitle(`Notification channels`)
            .setColor(this.hex)
            .setDescription(list.join('\n'))
            .setAuthor(message.author.username, message.author.avatarURL({dynamic:true}))
            .setFooter(`${list.length} channels`)
            if(list.length <= 10) {
                message.channel.send({ embeds: [embed] })
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, list);
            }
            return
        }
        const channels = await message.client.db.updates.findAll()
        let arr = []
        this.db.add(`UpdateCount`, 1)
        for (const channel of channels) {
            if (message.client.channels.cache.get(channel.channelID)) {
                const em = new MessageEmbed()
                .setTitle(`New update`)
                .setDescription(stripIndent`
    \`\`\`${args.join(' ')}\`\`\` 
    This message is to notify you about new features.
    To disable this message use ${message.prefix}updates none
    view all updates at https://slatt.gitbook.io/slatt-help/bot/recent-updates
    `)
                .setTimestamp()
                .setFooter(`Update #${this.db.get(`UpdateCount`)}`)
                .setColor(this.hex)
                .setAuthor(message.client.user.username, message.client.user.avatarURL())
                .setThumbnail(message.client.user.avatarURL())
        
                message.client.channels.cache.get(channel.channelID).send(
                    {embeds: [em]})
            } else {
                arr.push('{}')
            }
        }

        this.send_info(message, `Notified. failed to send to **${arr.length}** servers`)

    }
}