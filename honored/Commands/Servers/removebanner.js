const { MessageEmbed, Permissions } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'removebanner',
        aliases: ['delbanner'],
        syntax: 'removebanner',
        example: 'removebanner',
        description: 'Remove the banner from the server',
        module: 'servers',
        permissions: 'manage_guild',
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_GUILD')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                        .setColor(session.warn)
                ]
            });
        }
        
        if (!message.guild.banner) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: This server does not have a banner`)
                ]
            });
        }

        try {
            await message.guild.setBanner(null);
            const embed = new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: The server banner has been removed`);
            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error while removing server banner:', error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                ]
            });
        }
    }
};
