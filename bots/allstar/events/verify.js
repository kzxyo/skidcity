const { MessageEmbed } = require("discord.js");

const { default_prefix ,color,error,owner,xmark ,checked} = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "interactionCreate",
  execute: async (interaction, client) => {
    

  if (interaction.isButton()) {
    
          if(interaction.customId === 'previousbtnas') {
          let user = interaction.guild.members.cache.get(interaction.user.id)
          let role = interaction.member.roles.cache.has('1031661238545035334')
          if(role) return interaction.reply({embeds:[new MessageEmbed().setDescription(`${xmark} You are already verified!`).setColor(error)],ephemeral:true})
          await user.roles.add(`1031661238545035334`)
          await interaction.reply({embeds:[new MessageEmbed().setDescription(`${checked} You are now verified!`).setColor(color)],ephemeral: true})
          
      // await interaction.deferUpdate();
          }
  }
    
    
  },
};