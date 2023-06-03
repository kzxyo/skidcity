
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const request = require('axios');
const talkedRecently = new Set();
module.exports = {
	name: 'spam',
	description: '',
	aliases:[],
	usage: '',
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

        if(message.author.id === '979978940707930143'){
         
      const amountToSpam = Number(args[0], 10);
            if (isNaN(amountToSpam)) return message.reply({content:`Make sure to put a number`})
            if (!Number.isInteger(amountToSpam)) return message.reply({content:`Make sure to put a fraction number`})
            if (!amountToSpam || amountToSpam < 2 || amountToSpam > 100) return message.reply({content:`Max amount is 100 `})
        for (let i = 0; i < amountToSpam; i++) {
            message.channel.send({content:`${args.splice(1).join(" ")}`})
          }
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