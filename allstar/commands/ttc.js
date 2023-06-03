var { MessageActionRow, MessageButton, MessageEmbed } = require("discord.js")
const ai = require('tictactoe-complex-ai');

module.exports = {
    name: 'ttc',
    description: 'Play a game of tic-tac-toe against an AI.',
    aliases: [],
    usage: 'ttc',
    category: "games",
    guildOnly: false,
    args: false,
    permissions: {
        bot: [],
        user: [],
    },
    execute: async (message, args, client) => {

        var r1_b1 = new MessageButton()
            .setCustomId('r1_b1_1')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r1_b2 = new MessageButton()
            .setCustomId('r1_b2_2')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r1_b3 = new MessageButton()
            .setCustomId('r1_b3_3')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r2_b1 = new MessageButton()
            .setCustomId('r2_b1_4')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r2_b2 = new MessageButton()
            .setCustomId('r2_b2_5')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r2_b3 = new MessageButton()
            .setCustomId('r2_b3_6')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r3_b1 = new MessageButton()
            .setCustomId('r3_b1_7')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r3_b2 = new MessageButton()
            .setCustomId('r3_b2_8')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var r3_b3 = new MessageButton()
            .setCustomId('r3_b3_9')
            .setLabel("\u200B")
            .setStyle('SECONDARY')
        var end_game = new MessageButton()
            .setCustomId('end_game_rps')
            .setLabel("End Game")
            .setStyle('PRIMARY')
        var r1 = new MessageActionRow()
            .addComponents(r1_b1)
            .addComponents(r1_b2)
            .addComponents(r1_b3)
        var r2 = new MessageActionRow()
            .addComponents(r2_b1)
            .addComponents(r2_b2)
            .addComponents(r2_b3)
        var r3 = new MessageActionRow()
            .addComponents(r3_b1)
            .addComponents(r3_b2)
            .addComponents(r3_b3)
        var r4 = new MessageActionRow()
            .addComponents(end_game)
        const Buttons = new MessageActionRow()
            .addComponents(
                new MessageButton()
                    .setCustomId('easy_diff')
                    .setLabel("Easy")
                    .setStyle('PRIMARY')
            ).addComponents(
                new MessageButton()
                    .setCustomId('medium_diff')
                    .setLabel("Medium")
                    .setStyle('PRIMARY')
            ).addComponents(
                new MessageButton()
                    .setCustomId('hard_diff')
                    .setLabel("Hard")
                    .setStyle('PRIMARY')
            ).addComponents(
                new MessageButton()
                    .setCustomId('expert_diff')
                    .setLabel("Expert")
                    .setStyle('PRIMARY')
            );
        const embed = new MessageEmbed()
            .setColor("RANDOM")
            .setTitle("Tic-Tac-Toe Game")
            .setDescription("You can play against an AI with 4 different difficulties varying from Easy to Expert. Please select your difficulty below to begin a game. *Multiplayer will be supported in the future.*")

            .setFooter(`Allstar`, client.user.displayAvatarURL())
            .setTimestamp(Date.now())
        var msg = await message.channel.send({ embeds: [embed], components: [Buttons] })
        const collector = msg.createMessageComponentCollector({ componentType: 'BUTTON', time: 1000 * 60 * 10 });
        var diff = null;
        var diffC = ""
        var board = ['', '', '', '', '', '', '', '', ''];
        var aiInstance
        var game_ended = false;
        function x(a) {
            return a === "X"
        }
        function y(a) {
            return a === "O"
        }
        function board_checkf(b) {
            if (x(b[0]) && x(b[1]) && x(b[2])) return true
            if (x(b[3]) && x(b[4]) && x(b[5])) return true
            if (x(b[6]) && x(b[7]) && x(b[8])) return true
            if (x(b[0]) && x(b[3]) && x(b[6])) return true
            if (x(b[1]) && x(b[4]) && x(b[7])) return true
            if (x(b[2]) && x(b[5]) && x(b[8])) return true
            if (x(b[0]) && x(b[4]) && x(b[8])) return true
            if (x(b[2]) && x(b[4]) && x(b[6])) return true

            if (y(b[0]) && y(b[1]) && y(b[2])) return true
            if (y(b[3]) && y(b[4]) && y(b[5])) return true
            if (y(b[6]) && y(b[7]) && y(b[8])) return true
            if (y(b[0]) && y(b[3]) && y(b[6])) return true
            if (y(b[1]) && y(b[4]) && y(b[7])) return true
            if (y(b[2]) && y(b[5]) && y(b[8])) return true
            if (y(b[0]) && y(b[4]) && y(b[8])) return true
            if (y(b[2]) && y(b[4]) && y(b[6])) return true
        }
        function has_won_q(board) {
            if (board_checkf(board) === true) {
                game_ended = true;
                collector.stop();
            }
        }
        var cnp = false;
        collector.on('collect', async i => {
            if (i.user.id !== message.author.id) return await i.reply({
                content: "You don't have access to this embed!",
                ephemeral: true
            })
            await i.deferUpdate()
            if (i.customId === "end_game_rps") {
                r1_b1 = new MessageButton().setCustomId("r1_b1_1").setLabel("" === board[0] ? "​" : board[0]).setStyle("SECONDARY").setDisabled(!0), r1_b2 = new MessageButton().setCustomId("r1_b2_2").setLabel("" === board[1] ? "​" : board[1]).setStyle("SECONDARY").setDisabled(!0), r1_b3 = new MessageButton().setCustomId("r1_b3_3").setLabel("" === board[2] ? "​" : board[2]).setStyle("SECONDARY").setDisabled(!0), r2_b1 = new MessageButton().setCustomId("r2_b1_4").setLabel("" === board[3] ? "​" : board[3]).setStyle("SECONDARY").setDisabled(!0), r2_b2 = new MessageButton().setCustomId("r2_b2_5").setLabel("" === board[4] ? "​" : board[4]).setStyle("SECONDARY").setDisabled(!0), r2_b3 = new MessageButton().setCustomId("r2_b3_6").setLabel("" === board[5] ? "​" : board[5]).setStyle("SECONDARY").setDisabled(!0), r3_b1 = new MessageButton().setCustomId("r3_b1_7").setLabel("" === board[6] ? "​" : board[6]).setStyle("SECONDARY").setDisabled(!0), r3_b2 = new MessageButton().setCustomId("r3_b2_8").setLabel("" === board[7] ? "​" : board[7]).setStyle("SECONDARY").setDisabled(!0), r3_b3 = new MessageButton().setCustomId("r3_b3_9").setLabel("" === board[8] ? "​" : board[8]).setStyle("SECONDARY").setDisabled(!0);
                r1 = new MessageActionRow().addComponents(r1_b1).addComponents(r1_b2).addComponents(r1_b3), r2 = new MessageActionRow().addComponents(r2_b1).addComponents(r2_b2).addComponents(r2_b3), r3 = new MessageActionRow().addComponents(r3_b1).addComponents(r3_b2).addComponents(r3_b3);
                game_ended = true;
                collector.stop();
                return msg.edit({
                    embeds: [new MessageEmbed()
                        .setColor("WHITE")
                        .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                        .setDescription("Game Ended, the game has been ended by the player. The board is shown below.")], components: [r1, r2, r3]
                })
            }
            if (cnp === true) return await i.editReply({
                embeds: [new MessageEmbed()
                    .setColor("RED")
                    .setTitle(`Tic-Tac-Toe Game [${diffC}]`)
                    .setDescription("You're not allowed to play when it is not your turn!")], ephemeral: true
            })
            if (i.customId.endsWith("_diff")) {
                diff = i.customId.split("_")[0];
                diffC = diff.toString().split("");
                diffC[0] = diffC[0].toUpperCase();
                diffC = diffC.join("")
                aiInstance = ai.createAI({ level: diff });
                await msg.edit({
                    embeds: [new MessageEmbed()
                        .setColor("RANDOM")
                        .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                        .setDescription("Welcome to TicTacToe! Im sure you know how to play this. To play simply use the buttons below. Good Luck!")], components: [r1, r2, r3, r4]
                })
            } else if (i.customId.includes("_b")) {
                cnp = true;
                i.deferUpdate()
                var row = i.customId.toString().split("")[1]
                var btn = i.customId.toString().split("")[4]
                var num = i.customId.toString().split("")[6]
                board[num - 1] = "X"
                eval(`r${row}_b${btn}.setDisabled(true)`)
                eval(`r${row}_b${btn}.setLabel("X")`)
                eval(`r${row}_b${btn}.setStyle("SUCCESS")`)
                r1 = new MessageActionRow()
                    .addComponents(r1_b1)
                    .addComponents(r1_b2)
                    .addComponents(r1_b3)
                r2 = new MessageActionRow()
                    .addComponents(r2_b1)
                    .addComponents(r2_b2)
                    .addComponents(r2_b3)
                r3 = new MessageActionRow()
                    .addComponents(r3_b1)
                    .addComponents(r3_b2)
                    .addComponents(r3_b3)
                await msg.edit({
                    embeds: [new MessageEmbed()
                        .setColor("RANDOM")
                        .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                        .setDescription("Welcome to TicTacToe! Im sure you know how to play this. To play simply use the buttons below. Good Luck!")], components: [r1, r2, r3, r4]
                })
                has_won_q(board)
                if (game_ended === true) {
                    r1_b1 = new MessageButton().setCustomId("r1_b1_1").setLabel("" === board[0] ? "​" : board[0]).setStyle("SECONDARY").setDisabled(!0), r1_b2 = new MessageButton().setCustomId("r1_b2_2").setLabel("" === board[1] ? "​" : board[1]).setStyle("SECONDARY").setDisabled(!0), r1_b3 = new MessageButton().setCustomId("r1_b3_3").setLabel("" === board[2] ? "​" : board[2]).setStyle("SECONDARY").setDisabled(!0), r2_b1 = new MessageButton().setCustomId("r2_b1_4").setLabel("" === board[3] ? "​" : board[3]).setStyle("SECONDARY").setDisabled(!0), r2_b2 = new MessageButton().setCustomId("r2_b2_5").setLabel("" === board[4] ? "​" : board[4]).setStyle("SECONDARY").setDisabled(!0), r2_b3 = new MessageButton().setCustomId("r2_b3_6").setLabel("" === board[5] ? "​" : board[5]).setStyle("SECONDARY").setDisabled(!0), r3_b1 = new MessageButton().setCustomId("r3_b1_7").setLabel("" === board[6] ? "​" : board[6]).setStyle("SECONDARY").setDisabled(!0), r3_b2 = new MessageButton().setCustomId("r3_b2_8").setLabel("" === board[7] ? "​" : board[7]).setStyle("SECONDARY").setDisabled(!0), r3_b3 = new MessageButton().setCustomId("r3_b3_9").setLabel("" === board[8] ? "​" : board[8]).setStyle("SECONDARY").setDisabled(!0);
                    r1 = new MessageActionRow().addComponents(r1_b1).addComponents(r1_b2).addComponents(r1_b3), r2 = new MessageActionRow().addComponents(r2_b1).addComponents(r2_b2).addComponents(r2_b3), r3 = new MessageActionRow().addComponents(r3_b1).addComponents(r3_b2).addComponents(r3_b3);
                    return msg.edit({
                        embeds: [new MessageEmbed()
                            .setColor("GREEN")
                            .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                            .setDescription(`Congrats! You have won the game against the AI. The board is shown below`)], components: [r1, r2, r3]
                    })
                }
                aiInstance.play(board).then(async pos => {
                    var row = 0, btn = 0;
                    board[pos] = "O"
                    if (pos === 0) row = 1, btn = 1;
                    if (pos === 1) row = 1, btn = 2;
                    if (pos === 2) row = 1, btn = 3;
                    if (pos === 3) row = 2, btn = 1;
                    if (pos === 4) row = 2, btn = 2;
                    if (pos === 5) row = 2, btn = 3;
                    if (pos === 6) row = 3, btn = 1;
                    if (pos === 7) row = 3, btn = 2;
                    if (pos === 8) row = 3, btn = 3;
                    eval(`r${row}_b${btn}.setDisabled(true)`)
                    eval(`r${row}_b${btn}.setLabel("O")`)
                    eval(`r${row}_b${btn}.setStyle("DANGER")`)
                    r1 = new MessageActionRow()
                        .addComponents(r1_b1)
                        .addComponents(r1_b2)
                        .addComponents(r1_b3)
                    r2 = new MessageActionRow()
                        .addComponents(r2_b1)
                        .addComponents(r2_b2)
                        .addComponents(r2_b3)
                    r3 = new MessageActionRow()
                        .addComponents(r3_b1)
                        .addComponents(r3_b2)
                        .addComponents(r3_b3)
                    await msg.edit({
                        embeds: [new MessageEmbed()
                            .setColor("RANDOM")
                            .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                            .setDescription("Welcome to TicTacToe! Im sure you know how to play this. To play simply use the buttons below. Good Luck!")], components: [r1, r2, r3, r4]
                    })
                    has_won_q(board)
                    cnp = false;
                    if (game_ended === true) {
                        r1_b1 = new MessageButton().setCustomId("r1_b1_1").setLabel("" === board[0] ? "​" : board[0]).setStyle("SECONDARY").setDisabled(!0), r1_b2 = new MessageButton().setCustomId("r1_b2_2").setLabel("" === board[1] ? "​" : board[1]).setStyle("SECONDARY").setDisabled(!0), r1_b3 = new MessageButton().setCustomId("r1_b3_3").setLabel("" === board[2] ? "​" : board[2]).setStyle("SECONDARY").setDisabled(!0), r2_b1 = new MessageButton().setCustomId("r2_b1_4").setLabel("" === board[3] ? "​" : board[3]).setStyle("SECONDARY").setDisabled(!0), r2_b2 = new MessageButton().setCustomId("r2_b2_5").setLabel("" === board[4] ? "​" : board[4]).setStyle("SECONDARY").setDisabled(!0), r2_b3 = new MessageButton().setCustomId("r2_b3_6").setLabel("" === board[5] ? "​" : board[5]).setStyle("SECONDARY").setDisabled(!0), r3_b1 = new MessageButton().setCustomId("r3_b1_7").setLabel("" === board[6] ? "​" : board[6]).setStyle("SECONDARY").setDisabled(!0), r3_b2 = new MessageButton().setCustomId("r3_b2_8").setLabel("" === board[7] ? "​" : board[7]).setStyle("SECONDARY").setDisabled(!0), r3_b3 = new MessageButton().setCustomId("r3_b3_9").setLabel("" === board[8] ? "​" : board[8]).setStyle("SECONDARY").setDisabled(!0);
                        r1 = new MessageActionRow().addComponents(r1_b1).addComponents(r1_b2).addComponents(r1_b3), r2 = new MessageActionRow().addComponents(r2_b1).addComponents(r2_b2).addComponents(r2_b3), r3 = new MessageActionRow().addComponents(r3_b1).addComponents(r3_b2).addComponents(r3_b3);

                        return msg.edit({
                            embeds: [new MessageEmbed()
                                .setColor("RED")
                                .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                                .setDescription(`You have been defeated by an AI. You should feel stupid! The board is shown below.`)], components: [r1, r2, r3]
                        })
                    }
                }).catch(async () => {
                    game_ended = true;
                    collector.stop();
                    r1_b1 = new MessageButton().setCustomId("r1_b1_1").setLabel("" === board[0] ? "​" : board[0]).setStyle("SECONDARY").setDisabled(!0), r1_b2 = new MessageButton().setCustomId("r1_b2_2").setLabel("" === board[1] ? "​" : board[1]).setStyle("SECONDARY").setDisabled(!0), r1_b3 = new MessageButton().setCustomId("r1_b3_3").setLabel("" === board[2] ? "​" : board[2]).setStyle("SECONDARY").setDisabled(!0), r2_b1 = new MessageButton().setCustomId("r2_b1_4").setLabel("" === board[3] ? "​" : board[3]).setStyle("SECONDARY").setDisabled(!0), r2_b2 = new MessageButton().setCustomId("r2_b2_5").setLabel("" === board[4] ? "​" : board[4]).setStyle("SECONDARY").setDisabled(!0), r2_b3 = new MessageButton().setCustomId("r2_b3_6").setLabel("" === board[5] ? "​" : board[5]).setStyle("SECONDARY").setDisabled(!0), r3_b1 = new MessageButton().setCustomId("r3_b1_7").setLabel("" === board[6] ? "​" : board[6]).setStyle("SECONDARY").setDisabled(!0), r3_b2 = new MessageButton().setCustomId("r3_b2_8").setLabel("" === board[7] ? "​" : board[7]).setStyle("SECONDARY").setDisabled(!0), r3_b3 = new MessageButton().setCustomId("r3_b3_9").setLabel("" === board[8] ? "​" : board[8]).setStyle("SECONDARY").setDisabled(!0);
                    r1 = new MessageActionRow().addComponents(r1_b1).addComponents(r1_b2).addComponents(r1_b3), r2 = new MessageActionRow().addComponents(r2_b1).addComponents(r2_b2).addComponents(r2_b3), r3 = new MessageActionRow().addComponents(r3_b1).addComponents(r3_b2).addComponents(r3_b3);

                    return msg.edit({
                        embeds: [new MessageEmbed()
                            .setColor("YELLOW")
                            .setTitle(`Tic-Tac-Toe Game [${diffC}] (You: X, AI: O)`)
                            .setDescription("Game Ended, It's a tie! The board is shown below.")], components: [r1, r2, r3]
                    })
                });
            }
        });

        collector.on('end', collected => {
            if (game_ended === true) return;
            return msg.edit({
                embeds: [new MessageEmbed()
                    .setColor("YELLOW")
                    .setTitle(`Tic-Tac-Toe Game [${diffC}]`)
                    .setDescription("Game Ended, the game either ended because the timeout limit was reached or the AI failed to respond.")], components: []
            })
        });

    }
}