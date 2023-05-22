
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'shibe',
	description: 'returns an image of a random shibe',
	aliases:[],
	usage: '\```shibe \```',
  category: "image",
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
     axios.get(`http://shibe.online/api/shibes?count=${Math.floor(Math.random() * 100)}&urls=true`)
      
.then(response => {
      
  let embed = new MessageEmbed()
    .setImage(response.data[Math.floor(Math.random() * response.data.length)])
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