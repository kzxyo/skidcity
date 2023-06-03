
const{ MessageEmbed,MessageAttachment } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'meme',
	description: 'returns a funny meme',
	aliases:[],
	usage: '\```meme \```',
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
      axios.get(`https://luminabot.xyz/api/json/meme`)
      .then(response => {
        let embed = new MessageEmbed()
        .setURL(`${response.data.url}`)
        .setTitle(`${response.data.title}`)
        .setDescription(`:thumbsup: : ${response.data.upvotes} | 💬 : ${response.data.comments}`)
        .setImage(response.data.image)
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