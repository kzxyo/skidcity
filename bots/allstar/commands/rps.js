var util = require("../rps-logic/main.js")
var { MessageActionRow, MessageButton, MessageEmbed } = require("discord.js")
const game = require('@sinisterdev/rock-paper-scissor');

module.exports = {
	name: 'rps',
	description: 'Play a game of rock-paper-scissors with someone or with an AI!',
	aliases:[],
	usage: 'rps (user)',
  category: "games",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
   
   
   var rock = util.Buttons.rock;
  var scissors = util.Buttons.scissors
  var paper = util.Buttons.paper
  var Buttons = util.Buttons.Buttons
  var Accept = util.Buttons.Accept
  var Reject = util.Buttons.Reject
  var Start = util.Buttons.Start
  var Continue = util.Buttons.Continue
  var EndGame = util.Buttons.EndGame
  var TryAgain = util.Buttons.TryAgain
  var PlayAgain = util.Buttons.PlayAgain
  var sleep = util.Functions.sleep
  if (args.length !== 0) {
    var player2_id, player2_user, player1_id = message.author.id, player1_user = message.author.username, member = message.mentions.users.first(), player2_id = member.id, player2_user = member.username, round = 1; global.played = 0, global.p1_wins = 0, global.p2_wins = 0, global.already_played = [];
    if (member === undefined || member.bot === true || member.system === true)
      return message.channel.send({
        embeds: [util.Embeds.Initial(client)]
      })
    if (player1_id === player2_id) return message.channel.send({ embeds: [util.Embeds.SameUserChallenger(client)] })
    const embed = util.Embeds.Challenge(client, player1_id, player2_id)
    var msg = await message.channel.send({ embeds: [embed], components: [Accept, Reject] })
    const filter = i => i.user.id === player1_id || i.user.id === player2_id
    const collector = msg.createMessageComponentCollector({ filter, time: 1000 * 60 * 60 });
    collector.on("collect", async i => {
      console.log(i.customId + ' ' + i.user.tag)
      try {
        if (i.customId === "end") {
          var winner = util.Functions.CalcWinner(global.p1_wins, global.p2_wins, player1_user, player2_user)
          msg.edit({
            embeds: [util.Embeds.EndResults(client, player1_user, player2_user, global.p1_wins, global.p2_wins, round, winner)], components: []
          })
        }
        if (i.customId === "continue") {
          i.deferUpdate();
          return msg.edit({
            embeds: [util.Embeds.TimeToPlay(client, round)], components: [Buttons]
          })
        }
      
        if (["rock", "paper", "scissors"].includes(i.customId)) {
          if (global.already_played.includes(i.user.id)) return i.reply({ content: `You can't play if it's not your turn.`, ephemeral: true })
          global.already_played.push(i.user.id)
          global.played++
          if (i.user.id === player1_id) global.player1 = i.customId;
          if (i.user.id === player2_id) global.player2 = i.customId;
          i.reply({ content: `You have chosen ${i.customId}! Please wait for the other player to make their decision.`, ephemeral: true })
          if (global.played === 2) {
            global.already_played = []
            await msg.edit({
              embeds: [util.Embeds.multi_r(client)], components: []
            })
            await sleep(1000)
            await msg.edit({
              embeds: [util.Embeds.multi_p(client)], components: []
            })
            await sleep(1000)
            await msg.edit({
              embeds: [util.Embeds.multi_s(client)], components: []
            })
            await sleep(1000)
            var who_won = util.Functions.WhoWon(global.player1, global.player2)
            if (who_won === 0) msg.edit({
              embeds: [util.Embeds.Tie(client, player1_user, player2_user, global.p1_wins, global.p2_wins, round)], components: [Continue, EndGame]
            })
            if (who_won === 1) {
              global.p1_wins++; msg.edit({
                embeds: [util.Embeds.P1(client, player1_user, player2_user, global.p1_wins, global.p2_wins, round)], components: [Continue, EndGame]
              })
            }
            if (who_won === 2) {
              global.p2_wins++; msg.edit({
                embeds: [util.Embeds.P2(client, player1_user, player2_user, global.p1_wins, global.p2_wins, round)], components: [Continue, EndGame]
              })
            }
            round++; global.player1 = undefined; global.player2 = undefined; global.played = 0; return;
          }
        }
        if (["accept", "reject"].includes(i.customId) && i.user.id !== player2_id) return i.reply({
          embeds: [util.Embeds.ARError(client, player2_id)], ephemeral: true
        })
        if (i.customId === "reject") {
          i.deferUpdate();
          collector.stop();
          return msg.edit({
            embeds: [util.Embeds.R(client, player2_id)], components: []
          })
        }
        if (i.customId === "accept") return msg.edit({
          embeds: [util.Embeds.A(client)], components: [Start]
        })
        if (i.customId === "start" && i.user.id !== player1_id) return i.reply({
          embeds: [util.Embeds.StartError(client, player1_id)], ephemeral: true
        })
        if (i.customId === "start") {
          i.deferUpdate();
          return msg.edit({
            embeds: [util.Embeds.Start(client, round)], components: [Buttons]
          })
        }
      } catch (e) {
        try {
          msg.edit({
            embeds: [util.Embeds.MultiError(client)], components: []
          })
        } catch (y) { }
      }
    })
  } else {
    const embed = util.Embeds.AIEmbed(client)
    var msg = await message.channel.send({ embeds: [embed], components: [Buttons] })
    const filter = i => i.user.id === message.author.id;
    const collector = msg.createMessageComponentCollector({ filter, time: 1000 * 60 * 60 });
    var wins_player = 0, wins_comp = 0;
    collector.on('collect', async i => {
      try {
        await i.deferUpdate()
        if (i.customId === "try_again" || i.customId === "play_again") return await msg.edit({ embeds: [embed], components: [Buttons] })
        if (i.customId === "end") return await msg.edit({
          embeds: [util.Embeds.AIEnd(client, wins_player, wins_comp)], components: []
        })
        await msg.edit({
          embeds: [util.Embeds.r(client)], components: []
        })
        await sleep(1000)
        await msg.edit({
          embeds: [util.Embeds.p(client)], components: []
        })
        await sleep(1000)
        await msg.edit({
          embeds: [util.Embeds.s(client)], components: []
        })
        await sleep(1000)
        const result = game.play(i.customId);
        if (result.success === false || result.error !== null) return await msg.edit({
          embeds: [util.Embeds.AIE(client)], components: [TryAgain]
        })
        if (result.winner === "player") {
          wins_player++; return await msg.edit({
            embeds: [util.Embeds.PlayerWin(client, wins_player, wins_comp, i.customId, result.computer)], components: [PlayAgain, EndGame]
          })
        }
        if (result.winner === "computer") {
          wins_comp++; return await msg.edit({
            embeds: [util.Embeds.CompWin(client, wins_player, wins_comp, i.customId, result.computer)], components: [PlayAgain, EndGame]
          })
        }
        if (result.winner === "tie") return await msg.edit({
          embeds: [util.Embeds.TieAI(client, wins_player, wins_comp, i.customId, result.computer)], components: [PlayAgain, EndGame]
        })
      } catch (e) {

      }
    });
    collector.on("end", async e => {
      await msg.edit({
        embeds: [util.Embeds.AIEnded(client)], components: []
      })
    })
  }
   
   
   }
   }