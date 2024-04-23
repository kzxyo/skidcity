const moment = require("moment");
const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'reactionsnipe',
        description: 'Snipe a recently removed reaction',
        aliases: ["rs"],
        syntax: 'reactionsnipe',
        example: 'reactionsnipe',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const reactionSnipes = session.reactionSnipes.get(message.channel.id);

            if (!reactionSnipes || reactionSnipes.length === 0) {
                const errorEmbed = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There is no reaction to snipe`);
                return await message.channel.send({ embeds: [errorEmbed] });
            }

            const latestReactionSnipe = reactionSnipes[0];

            const { message: reactedMessage, reaction, user, removedAt } = latestReactionSnipe;

            if (!reactedMessage || !reaction || !user) {
                throw new Error('Message, reaction, or user not found');
            }

            const username = user.username;
            const avatar = user.displayAvatarURL({ dynamic: true });

            const embed = new MessageEmbed()
                .setAuthor(`${username}`, avatar)
                .setDescription(`Reaction removed from [this message](${reactedMessage.url})`)
                .addField('Reacted Emoji', reaction.emoji.toString(), true)
                .addField('Reacted By', user.toString(), true)
                .setColor(session.color)
                .setFooter(`Removed ${moment(removedAt).fromNow()}`);

            await message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error while reaction sniping:', error);
        }
    }
};
