
const{ MessageEmbed } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'joinlock',
	description: 'locks the server(kicks every new member)',
	aliases:[],
	usage: '\```YAML\n\njoinlock [on/off] \```',
  category: "security",
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
              let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error)

        const authorized = [
            message.guild.ownerId,
            owner,
          "839221856976109608",
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
     if (!authorized.includes(message.author.id)) return message.reply({embeds:[onlyown]});
      
      if(args[0] === 'on'){
        db.set(`joinlock_${message.guild.id}`,true)
        message.reply({embeds:[
          new MessageEmbed()
          .setDescription(`${checked} Join lock is now enabled`)
          .setColor(color)
        ]})
      }
      else if(args[0] === 'off'){
        db.delete(`joinlock_${message.guild.id}`)
         message.reply({embeds:[
          new MessageEmbed()
          .setDescription(`${checked} Join lock is now disabled`)
          .setColor(color)
        ]})
      }

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};