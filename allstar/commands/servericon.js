
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'servericon',
	description: 'returns server icon',
	aliases:["guildicon"],
	usage: '\```YAML\n\n servericon \``` ',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
        
            if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

          let embed = new MessageEmbed()
          .setImage((message.guild.iconURL({ format: "png", dynamic: true, size: 4096 })))
          .setFooter({ text: `${message.guild.name}`})
          .setColor(color)
          await message.reply({embeds:[embed]}).catch(() => {/*Ignore error*/})
      
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};