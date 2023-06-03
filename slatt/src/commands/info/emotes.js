const Command = require('../Command.js');
const Discord = require('discord.js')
const ReactionMenu = require('../ReactionMenu.js');
const { stripIndent } = require('common-tags');

module.exports = class emotes extends Command {
    constructor(client) {
        super(client, {
            name: 'emotes',
            aliases: ['ems', 'emojis'],
            usage: 'emotes',
            type: client.types.INFO,
            description: 'View recent emotes',
        });
    }
    async run(message, args) {
        let messages
        if (!args.length) {
            messages = (await message.channel.messages.fetch({ limit: 50 })).filter(x => x.content.match(/(?<=<?a?:?\w{2,32}:)\d{17,19}(?=>?)/gi))
            if (!messages.size) return this.send_error(message, 1, `No emojis within the last **50** messages`)
            messages = messages
            const arr = []
            messages.forEach(msg => {
                if (msg.content) {
                    const rgx = msg.content.match(/<:.+:(\d+)>/gm) || msg.content.match(/<a:.+:(\d+)>/gm)
                    const emote = Discord.Util.parseEmoji(rgx[0])
                    if (emote) {
                        arr.push({ emote: emote, msg: msg })
                    }
                }
            })
            let n = 0
            const embed = new Discord.MessageEmbed()
                .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                .setTitle(`Emoji: ${arr[n].emote.name}`)
                .setDescription(stripIndent`
                URL: **[${arr[n].emote.name}](https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"})**
                Message: **[Jump](${arr[n].msg.url})**
                `)
                .setImage(`https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"}`)
                .setColor(this.hex)
                .setFooter(`Viewing: ${n + 1}/${arr.length}`)
            const json = embed.toJSON();
            const previous = () => {
                (n <= 0) ? n = arr.length - 1 : n--;
                return new Discord.MessageEmbed(json)
                    .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                    .setTitle(`Emoji: ${arr[n].emote.name}`)
                    .setDescription(stripIndent`
                    URL: **[${arr[n].emote.name}](https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"})**
                    Message: **[Jump](${arr[n].msg.url})**
                    `)
                    .setImage(`https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"}`)
                    .setColor(this.hex)
                    .setFooter(`Viewing: ${n + 1}/${arr.length}`)
            };
            const next = () => {
                (n >= arr.length - 1) ? n = 0 : n++;
                return new Discord.MessageEmbed(json)
                    .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                    .setTitle(`Emoji: ${arr[n].emote.name}`)
                    .setDescription(stripIndent`
                    URL: **[${arr[n].emote.name}](https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"})**
                    Message: **[Jump](${arr[n].msg.url})**
                    `)
                    .setImage(`https://cdn.discordapp.com/emojis/${arr[n].emote.id}.${arr[n].emote.animated ? "gif" : "png"}`)
                    .setFooter(`Viewing: ${n + 1}/${arr.length}`)
                    .setColor(this.hex)
            };

            const reactions = {
                'LEFT_ARROW': previous,
                'STOP': null,
                'RIGHT_ARROW': next,
            };

            const menu = new ReactionMenu(
                message.client,
                message.channel,
                message.member,
                embed,
                null,
                null,
                reactions,
                180000
            );
            menu.reactions['⏹️'] = menu.stop.bind(menu);
        }
    }
}