const { Permissions, MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'softban',
        aliases: ['sb'],
        description: 'Bans a user then unbans instantly',
        syntax: 'softban [member]',
        example: 'softban @user',
        permissions: 'ban_members',
        parameters: 'member',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`ban_members\``)
                        .setColor(session.warn)
                ]
            });
        }
        const user = message.mentions.members.first();

        if (!user) {
            return displayCommandInfo(module.exports, session, message);
        }

        if (user.guild.id !== message.guild.id) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You can only ban users from your own server`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            await user.ban({ days: 7, reason: 'Softban' });
            await message.guild.members.unban(user, 'Softban');
            
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: ${user} has been softbanned`)
                ]
            });
        } catch (error) {
            console.error('Error executing softban:', error);
            message.channel.send(`An error occurred while executing the softban: ${error.message}`);
        }
    }
};
