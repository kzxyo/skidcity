const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration : {
        commandName: 'stealbanner',
        aliases: ['stealb'],
        description: 'Steal the banner of another server using its invite',
        syntax: 'stealbanner <invite code>',
        example: 'stealbanner okay',
        permissions: 'manage_guild',
        parameters: 'invite',
        module: 'servers',
    },

    run: async (session, message, args) => {

        if (!message.member.permissions.has('MANAGE_GUILD')) {

            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                ]
            });
        }

        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }

        let invite = await message.client.fetchInvite(args[0]).catch(() => {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Invalid invite code`)
                        .setColor(session.warn)
                ]
            });
        });

        let guild = invite.guild;
        let banner = guild.bannerURL({ format: 'png', size: 1024 });

        if (!banner) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: That server does not have a banner`)
                        .setColor(session.warn)
                ]
            });
        }

        message.guild.setBanner(banner).then(() => {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.grant} ${message.author}: Successfully set the banner to the stolen banner`)
                        .setColor(session.green)
                ]
            });
        }).catch(error => {
            console.error('Error setting banner:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Failed to set the banner`)
                        .setColor(session.warn)
                ]
            });
        });
    }
}
