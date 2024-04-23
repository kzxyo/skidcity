const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'stealemoji',
        aliases: ['addemoji', 'steal'],
        description: 'Add an emoji to your server',
        syntax: 'stealemoji [emoji]',
        example: 'stealemoji :rofl:',
        permissions: 'manage_emojis',
        module: 'utility'
    },

    run: async (session, message, args) => {
        if (!args[0] || !args[0].match(/<(a?):(\w+):(\d+)>/)) {
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

        try {
            const emoji = args[0].match(/<(a?):(\w+):(\d+)>/);
            await message.guild.emojis.create(`https://cdn.discordapp.com/emojis/${emoji[3]}.${emoji[1] ? 'gif' : 'png'}`, emoji[2]);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: Successfully added the emoji **${emoji[2]}**`)
                ]
            });
        } catch (error) {
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Failed to add the emoji`)
                        .setColor(session.warn)
                ]
            });
        }
    }
};
