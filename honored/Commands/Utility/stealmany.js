const { MessageEmbed, Permissions } = require('discord.js');
const moment = require('moment');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'stealmany',
        aliases: ['addmany'],
        description: 'Add multiple emojis to your server',
        syntax: 'stealmany [emoji] [emoji] [emoji]',
        example: 'stealmany :rofl: :meow: :gang:',
        permissions: 'manage_emojis',
        module: 'utility'
    },

    run: async (session, message, args) => {
        const emojiRegex = /<(a?):(\w+):(\d+)>/;
        const emojis = args.map(arg => {
            const match = arg.match(emojiRegex);
            if (!match) return null;
            return {
                animated: Boolean(match[1]),
                name: match[2],
                id: match[3]
            };
        }).filter(Boolean);

        if (!emojis.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_EMOJIS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_emojis\``)
                        .setColor(session.warn)
                ]
            });
        }

        const success = [];
        const fail = [];

        for (const emoji of emojis) {
            try {
                await message.guild.emojis.create(`https://cdn.discordapp.com/emojis/${emoji.id}.${emoji.animated ? 'gif' : 'png'}`, emoji.name);
                success.push(emoji.name);
            } catch (error) {
                fail.push(emoji.name);
            }
        }

        const embed = new MessageEmbed()
            .setColor(session.green)
            .setDescription(`${session.grant} ${message.author}: Successfully added ${success.length} emojis`);

        if (success.length) {
            embed.addField('Added', success.join('\n'), true);
        }

        if (fail.length) {
            embed.addField('Failed', fail.join('\n'), true);
        }

        message.channel.send({ embeds: [embed] });
    }
};
