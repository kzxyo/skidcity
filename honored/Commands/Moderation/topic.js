const { Permissions, MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'topic',
        aliases: ['none'],
        description: 'Set the topic of a channel',
        syntax: 'topic [channel] (topic)',
        example: 'topic #chat lvl 5 for pic',
        permissions: 'manage_channels',
        parameters: 'channel, text',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_channels\``)
                        .setColor(session.warn)
                ]
            });
        }

        const channelMention = message.mentions.channels.first();
        if (!channelMention) {
            return displayCommandInfo(module.exports, session, message);
        }

        if (channelMention.guild.id !== message.guild.id) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You can only set the topic for channels within your own server`)
                        .setColor(session.warn)
                ]
            });
        }

        const topic = args.slice(1).join(' ');

        try {
            await channelMention.setTopic(topic);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: I have set a new topic for ${channelMention}`)
                ]
            });
        } catch (error) {
            console.error('Error setting topic:', error);
            message.channel.send(`An error occurred while setting the topic: ${error.message}`);
        }
    }
};
