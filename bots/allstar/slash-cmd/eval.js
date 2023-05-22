const {
    MessageEmbed
  } = require('discord.js');
  const { SlashCommandBuilder } = require('@discordjs/builders');
  var hastebin = require('hastebin')
  async function eval_clean(text) {
    if (text && text.constructor.name == "Promise") text = await text
    if (typeof text !== "string")
      text = require("util").inspect(text, {
        depth: 1
      });
    text = text
      .replace(/`/g, "`" + String.fromCharCode(8203))
      .replace(/@/g, "@" + String.fromCharCode(8203));
    return text;
  }
  module.exports.runCmd = async (client, interaction) => {
    try {
      var code = interaction.options.getString('code');
      var message = await interaction.fetchReply();
      const evaled = eval(code);
      const cleaned = await eval_clean(evaled);
      if (cleaned.toString().length > 1000) {
        hastebin.createPaste(cleaned, {
          raw: false,
          contentType: 'text/plain',
          server: 'https://hastebin.com'
        }, {})
          .then(function(urlToPaste) {
            var input = code
            if (input.toString().length > 1000) input = "Not Available."
            var success_embed = new MessageEmbed()
              .setColor(0x00FF00)
              .setTitle('Code Executed Successfully')
              .addFields({
                name: 'Status: ',
                value: '**Executed**'
              }, {
                name: 'Input: ',
                value: `${input}`
              }, {
                name: 'Result: ',
                value: `HasteBin URL: ${urlToPaste}`
              })
              .setTimestamp()
              .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
              });
            interaction.editReply({
              embeds: [success_embed]
            })
          })
          .catch(function(requestError) {
            var input = code
            if (input.toString().length > 1000) input = "Not Available."
            var error_embed = new MessageEmbed()
              .setColor(0xFF0000)
              .setTitle('Code Execution Failed')
              .addFields({
                name: 'Status: ',
                value: '**Failed**'
              }, {
                name: "Error Type: ",
                value: `**_HasteBin Error_**`
              }, {
                name: "Input: ",
                value: `${input}`
              }, {
                name: 'Error: ',
                value: `${error.toString()}`
              })
              .setTimestamp()
              .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
              });
            interaction.editReply({
              embeds: [error_embed]
            })
          })
      } else {
        var input = code
        if (input.toString().length > 1000) input = "Not Available."
        var success_normal_embed = new MessageEmbed()
          .setColor(0x00FF00)
          .setTitle('Code Executed Successfully')
          .addFields({
            name: 'Status: ',
            value: '**Executed**'
          }, {
            name: 'Input: ',
            value: `${input}`
          }, {
            name: 'Result: ',
            value: `${cleaned.toString()}`
          })
          .setTimestamp()
          .setFooter({
            text: `${client.user.username}`,
            iconURL: client.user.displayAvatarURL()
          });
        interaction.editReply({
          embeds: [success_normal_embed]
        })
      }
    } catch (e) {
      var input = code
      if (input.toString().length > 1000) input = "Not Available."
      var error_type = "Error"
      if (e.toString().split(":").length !== 0) error_type = e.toString().split(":")[0]
      var error_normal_embed = new MessageEmbed()
        .setColor(0xFF0000)
        .setTitle('Code Execution Failed')
        .addFields({
          name: 'Status: ',
          value: '**Failed**'
        }, {
          name: "Error Type: ",
          value: `**${error_type}**`
        }, {
          name: "Input: ",
          value: `${input}`
        }, {
          name: 'Error: ',
          value: `${e.toString()}`
        })
        .setTimestamp()
        .setFooter({
          text: `${client.user.username}`,
          iconURL: client.user.displayAvatarURL()
        });
      interaction.editReply({
        embeds: [error_normal_embed]
      })
    }
  }
  module.exports.slashCmd = new SlashCommandBuilder()
    .setName('eval')
    .setDescription('Executes code on behalf of the bot.')
    .addStringOption(option =>
      option.setName('code')
        .setDescription('The code you want to execute.')
        .setRequired(true))
  module.exports.info = {
    "name": "eval",
    "description": "Executes code on behalf of the bot.",
    "usage": "eval <code>",
    "category": "Owner",
    "perms": ["Bot Owner"]
  }