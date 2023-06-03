
const{ MessageEmbed,MessageAttachment } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: '8ball',
	description: 'returns an answer to a question',
	aliases:[],
	usage: '\```8ball {question} \```',
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
      axios.get(`https://luminabot.xyz/api/json/8ball?text=${args.join(" ")}`)
      .then(response => {
        message.reply({embeds:[
        new MessageEmbed()
          .setDescription(`> **Question** ${response.data.question} \n>  **Answer** \`${response.data.answer}\``)
          .setFooter({text:`question asked by ${message.author.username}`})
          .setColor(color)
      ]})
      
    })
      
      /*
        let embed = new MessageEmbed()
        .setURL(`${response.data.url}`)
        .setTitle(`${response.data.title}`)
        .setDescription(`<:down2:1010942456562462750> : ${response.data.upvotes} | <:Message:1010885858792067192> : ${response.data.comments}`)
        .setImage(response.data.image)
        .setColor(color)
      
      message.reply({embeds:[embed]})
      
      */
     

      
  }

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    

	},
};