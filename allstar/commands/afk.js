
const{ MessageEmbed } = require('discord.js');
const db = require('quick.db')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'afk',
	description: 'returns afk message when someone pings you',
	aliases:[],
	usage: ' \```YAML\n\n afk {status}\``` ',
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

    
        const content = args.join(" ") ? args.join(' ') : "AFK"
        await db.set(`afktime-${message.author.id}+${message.guild.id}`,Date.now())
        await db.set(`afk-${message.author.id}+${message.guild.id}`, content)
        const embed = new MessageEmbed()
        .setColor(color)
        .setAuthor({name:`${message.author.username} went AFK`,iconURL:`${message.author.displayAvatarURL({dynamic:true,size:4096})}`})
        .setDescription(` \n **Status**  \n <:allstarreply:1032192256192553030>  ${content}`)

        message.reply({embeds:[embed]}).catch(() => {/*Ignore error*/})
              talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
    

	},
};