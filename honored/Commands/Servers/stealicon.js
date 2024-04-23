const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration : {
        commandName: 'stealicon',
        aliases: ['steali'],
        description: 'Steal the icon of another server using its invite',
        syntax: 'stealicon <invite code>',
        example: 'stealicon okay',
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
            let icon = guild.iconURL({ format: 'png', size: 1024 });
    
            if (!icon) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: That server does not have an icon`)
                            .setColor(session.warn)
                    ]
                });
            }
    
            message.guild.setIcon(icon).then(() => {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: Successfully set the icon to the stolen icon`)
                            .setColor(session.green)
                    ]
                });
            });
        }
    }