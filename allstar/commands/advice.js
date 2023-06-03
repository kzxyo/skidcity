
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'advice',
	description: 'gives you an advice',
	aliases:[],
	usage: '\```advice \```',
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
     axios.get(`https://luminabot.xyz/api/json/advice`)
      
.then(response => {
      
  let embed = new MessageEmbed()
    .setDescription('\```' + response.data.advice + '\```')
    .setColor(color)
           message.reply({embeds:[embed]})
     })



        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};