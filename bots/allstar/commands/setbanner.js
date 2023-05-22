
const{ MessageEmbed,Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'setbanner',
	description: 'set a banner for the server',
	aliases:["setguildbanner"],
	usage: '\```YAML\n\n setbanner [image.jpg/link]  \``` ',
  category: "moderation",
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
              let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error)

        
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});
    
         let icon = message.attachments.first().url || args[0]
         let done = new MessageEmbed()
          .setDescription(`${checked} Succesfully Updated Server Banner`)
          .setColor(color)

          let embed = new MessageEmbed()
          .setDescription(`${xmark} You need to provide a valid URL`)
          .setColor(color)
          if (!icon) return message.reply({embeds:[embed]}).catch(() => {/*Ignore error*/})
          
       if (message.attachments.first()) {
      icon = message.attachments.first().url
      message.guild.setBanner(icon).then(() => {
        return message.reply({embeds:[done]})
      })
    } 
      else {
      if (!icon) return message.reply({embeds:[embed]}).catch(() => {/*Ignore error*/});
      message.guild.setBanner(icon).then(() => {
        return message.reply({embeds:[done]})
      })
        
        
      } 
      
      
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};