const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'membercount',
        aliases: ['mc', 'members'],
        description: 'Shows member count.',
        syntax: 'membercount',
        example: 'membercount',
        module: 'information',
        devOnly: false
    },
    run: async (client, message, args) => {
        const usercount = message.guild.memberCount;
        const botcount = message.guild.members.cache.filter(m => m.user.bot).size;
        const humans = usercount - botcount;

        const embed = new MessageEmbed()
            .setColor('#2b2d31')
            .setAuthor(`${message.guild.name} member statistics`, message.guild.iconURL({ dynamic: true }))
            .addFields(
                { name: 'Members', value: `${message.guild.memberCount}`, inline: true },
                { name: 'Robots', value: `${message.guild.members.cache.filter(member => member.user.bot).size}`, inline: true },
                { name: 'Boosts', value: `${message.guild.premiumSubscriptionCount || '0'}`, inline: true },
            );

        message.channel.send({ embeds: [embed] });
    }
};
