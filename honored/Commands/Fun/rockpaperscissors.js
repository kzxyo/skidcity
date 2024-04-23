const { MessageEmbed, MessageActionRow, MessageButton } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'rockpaperscissors',
        aliases: ['rps'],
        description: 'Play rock paper scissors with another user',
        syntax: 'rockpaperscissors <member>',
        example: 'rockpaperscissors @x6l',
        parameters: 'member',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const mentionedUser = message.mentions.users.first();
        if (!mentionedUser || mentionedUser.bot || mentionedUser.id === message.author.id) {
            return displayCommandInfo(module.exports, session, message);
        }

        const buttonsRow = new MessageActionRow()
            .addComponents(
                new MessageButton()
                    .setCustomId('rock')
                    .setLabel('Rock')
                    .setStyle('SECONDARY'),
                new MessageButton()
                    .setCustomId('paper')
                    .setLabel('Paper')
                    .setStyle('SECONDARY'),
                new MessageButton()
                    .setCustomId('scissors')
                    .setLabel('Scissors')
                    .setStyle('SECONDARY')
            );

        const embed = new MessageEmbed()
            .setColor(session.color)
            .setTitle('Rock-Paper-Scissors')
            .setDescription(`${message.author} vs ${mentionedUser}`)
            .setTimestamp();

        const reply = await message.channel.send({ embeds: [embed], components: [buttonsRow] });

        const collector = reply.createMessageComponentCollector({
            filter: i => (i.user.id === message.author.id || i.user.id === mentionedUser.id) && !i.user.bot,
            time: 60000,
            max: 2
        });

        let userChoice, opponentChoice;

        collector.on('collect', async i => {
            const choice = i.customId;
            if (i.user.id === message.author.id) {
                userChoice = choice;
            } else if (i.user.id === mentionedUser.id) {
                opponentChoice = choice;
            }

            if (userChoice && opponentChoice) {
                collector.stop();
            }

            i.reply({ content: `You selected: ${choice}`, ephemeral: true });
        });

        collector.on('end', async collected => {
            const winner = calculateWinner(userChoice, opponentChoice);
            let result;

            if (winner === 'user') {
                result = `${message.author} wins!`;
            } else if (winner === 'opponent') {
                result = `${mentionedUser} wins!`;
            } else {
                result = 'It\'s a tie!';
            }

            embed.fields = [{ name: 'Result', value: result }, { name: 'Match Details', value: `${message.author}: ${userChoice}\n${mentionedUser}: ${opponentChoice}` }];
            if (reply && !reply.deleted) {
                reply.edit({ embeds: [embed], components: [] }).catch(console.error);
            }
        });
    }
};

function calculateWinner(userChoice, opponentChoice) {
    if ((userChoice === 'rock' && opponentChoice === 'scissors') ||
        (userChoice === 'paper' && opponentChoice === 'rock') ||
        (userChoice === 'scissors' && opponentChoice === 'paper')) {
        return 'user';
    } else if (userChoice === opponentChoice) {
        return 'tie';
    } else {
        return 'opponent';
    }
}
