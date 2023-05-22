
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'membercount',
	description: 'returns server membercount',
	aliases:["mc"],
	usage: ' \```YAML\n\n membercount \``` ',
  category: "information",
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
        //.addField(`memberCount`,`***${message.guild.memberCount}***`)
        .addField(`Member Count `,`**Total ${message.guild.memberCount} **\n>  <:allstarhumans:996652234261659718> Humans : ${message.guild.memberCount - message.guild.members.cache.filter(member => member.user.bot).size} \n> <:allstarbots:996652601170993202> Bots : ${message.guild.members.cache.filter(member => member.user.bot).size}`)
        .setColor(color)
         message.reply({embeds:[embed]}); 
      
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};