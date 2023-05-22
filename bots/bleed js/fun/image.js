const Discord = require('discord.js');
const gis = require('g-i-s');
const { color } = require("../../config.json");

module.exports = {
  name: "image",
  aliases: ["im", "img"],

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    message.channel.startTyping();
    let googleIcon = 'https://maxcdn.icons8.com/Share/icon/Logos//google_logo1600.png';

    const embed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: image')
    .setDescription('Search google for an image')
    .addField('**Aliases**', 'im, img', true)
    .addField('**Parameters**', 'member', true)
    .addField('**Information**', `N/A`, true)
    .addField('**Usage**', '\`\`\`Syntax: image <search>\nExample: image Ash Kaash\`\`\`')
    .setFooter(`Module: fun`)
    .setTimestamp()
    .setColor(color)
    message.channel.stopTyping(true);
  if (!args[0]) return message.channel.send(embed)

  message.channel.startTyping();
    const filter = (reaction, user) => user.id === message.author.id && (reaction.emoji.name === '⬅️' || reaction.emoji.name === '➡️');
    let page = 0
    let reactionTrigger = 0;
    let search = message.content.substring(message.content.indexOf(' ') + 1, message.content.length) || null;
    if (!search) {
      return message.channel.send('You need to type something to seach for this command to work')
    };
    async function reactionCatcher(msg) {
      var removeAll = setTimeout(function () {
        msg.reactions.removeAll();
      }, 60000)
      msg.awaitReactions(filter, { max: 1, time: 60000 }).then(collected => {
        if (collected) {
          if (collected.first().emoji.name === '➡️') {
            page++
            clearTimeout(removeAll);
            msg.reactions.removeAll()
            updateImg(msg);
          }
          if (collected.first().emoji.name === '⬅️') {
            page--
            clearTimeout(removeAll);
            msg.reaction.removeAll()
            updateImg(msg);
          }
        }
      });
    };
    async function generateReactions(msg) {
      if (page + 1 > 1 && page + 1 < 100) {
        msg.react('⬅️');
        setTimeout(function () {
          msg.react('➡️');
        }, 750)
      } else if (page == 0) {
        msg.react('➡️');
      } else if (page + 1 == 100) {
        msg.react('⬅️');
      }
      if (reactionTrigger !== 0) {
        reactionCatcher(msg)
      }
    };

    async function updateImg(msg) {
      gis(search, logResults);
      function logResults(error, results) {
        if (error) {
          console.log(error)
        }
        else {
          if (msg == null) {
            var embed = new Discord.MessageEmbed()
              .setColor(mentionedMember.displayHexColor || color)
              .setAuthor(message.author.username, message.author.avatarURL({
                dynamic: true
              }))
              .setTitle(`**Search Results for ${search}**`)
              .setImage(results[page].url)
              .setFooter(`${page + 1}/${results.length} of Google Image Search Results (Random)`, googleIcon);
            message.channel.stopTyping(true);
            message.channel.send(embed).then(msg => {
              generateReactions(msg);
              reactionCatcher(msg);
            });
          } else {
            var embed = new Discord.MessageEmbed()
              .setColor(mentionedMember.displayHexColor || color)
              .setAuthor(message.author.username, message.author.avatarURL({
                dynamic: true
              }))
              .setTitle(`**Search Results for ${search}**`)
              .setImage(results[page].url)
              .setFooter(`${page + 1}/${results.length} of Google Image Search Results (Random)`, googleIcon);
            msg.edit(embed)
            setTimeout(function () {
              generateReactions(msg)
              reactionCatcher(msg)
            }, 300)

          }
        }

      }
    }
    updateImg(null);
  }
};