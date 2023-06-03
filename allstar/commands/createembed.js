
const{ MessageEmbed,EmbedBuilder } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const parse = require('../regex.js')
const talkedRecently = new Set();
module.exports = {
	name: 'createembed',
	description: 'create an embed in json code',
	aliases:['embed','ce'],
	usage: '\```createembed {"description":"hi"} \```',
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
      
      
           try{
               await message.channel.send({embeds:[JSON.parse(args.join(' '))]})
           } catch(error){
             message.channel.send({embeds:[{description:`${xmark} ${error}`,color:"#F7C91D"}]})
           }


      
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};