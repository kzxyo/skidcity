
const{ MessageEmbed,MessageButton, MessageActionRow } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner,xmark,checked } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'clearnames',
	description: 'clears your name history',
	aliases:[],
	usage: '\```clearnames \```',
  category : 'utility',
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
  let pingemoji = `<:allstarconnection:996699189432025180>`

        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

            

        db.delete(`names_${message.author.id}`) 
    message.reply({
       embeds:[
        {
            description:`${checked} cleared your name history `,
            color:color
        }
         ] })

      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};