const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'avatar',
        aliases: ['av'],
        description: 'Show the avatar of a specified user.',
        syntax: 'avatar [user]',
        example: 'avatar @x6l',
        parameters: 'member',
        module: 'information',
        devOnly: false
    },
    run: async (session, message, args) => {
        
        let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

        if (!mentionedMember) {
            const searchName = args.join(' ').toLowerCase();
            mentionedMember = message.guild.members.cache.find(member =>
                member.user.username.toLowerCase() === searchName ||
                member.displayName.toLowerCase() === searchName
            );
        }

        const user = mentionedMember?.user || message.author;

        const topRole = message.member.roles.highest;

        const embed = new MessageEmbed()
            .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
            .setTitle(user.username + "'s avatar")
            .setURL(user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
            .setImage(user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
            .setColor(topRole ? topRole.hexColor : session.color);

        message.channel.send({ embeds: [embed] });
    }
};
