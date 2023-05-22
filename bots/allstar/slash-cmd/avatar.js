const { SlashCommandBuilder } = require('@discordjs/builders');
const { MessageEmbed, MessageActionRow, MessageButton } = require('discord.js');
var fs = require('fs');
const { normalize } = require('path');
const { description } = require('../commands/usage');
module.exports.name = "avatar";
module.exports.slashCmd = new SlashCommandBuilder()
  .setName('avatar')
  .setDescription('Displays mentioned user or your profiles profile picture')
  .addUserOption(option =>
    option
      .setName('target')
      .setDescription('The user\'s avatar to show')
      .setRequired(false))
module.exports.runCmd = async (client, interaction, generalData) => {

  const user = interaction.options.getUser('target') || interaction.user;

  const row = new MessageActionRow()
    .addComponents(
      new MessageButton()
        .setLabel('webp')
        .setEmoji("<:MessageLink:1010885859735785553>")
        .setURL(`${user.displayAvatarURL({ format: "webp", dynamic: true, size: 4096 })}`)
        .setStyle('LINK'),
    )
    .addComponents(
      new MessageButton()
        .setLabel('jpg')
        .setEmoji("<:MessageLink:1010885859735785553>")
        .setURL(`${user.displayAvatarURL({ format: "jpg", dynamic: true, size: 4096 })}`)
        .setStyle('LINK'),
    )
    .addComponents(
      new MessageButton()
        .setLabel('png')
        .setEmoji("<:MessageLink:1010885859735785553>")
        .setURL(`${user.displayAvatarURL({ format: "png", dynamic: true, size: 4096 })}`)
        .setStyle('LINK'),
    )
  let embed = new MessageEmbed()
    .setImage((user.displayAvatarURL({ format: "png", dynamic: true, size: 4096 })))
    .setFooter({ text: `${user.tag}` })
    .setColor("#7289da")
  await generalData.message.edit({ embeds: [embed], components: [row],ephemeral:true }).catch(() => {/*Ignore error*/ })



}
module.exports.info = {
  "name": "avatar",
  "description": "Displays mentioned user or your profiles profile picture",
  "usage": "avatar (user)",
  "category": "Utility",
  "perms": []
}