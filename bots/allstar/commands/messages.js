
const{ MessageEmbed } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'messages',
	description: 'returns user message count',
	aliases:['msgs'],
	usage: '\```messages\```',
  category: "utility",
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

      let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])
 
               if(!mentionedMember) {
      
      let data = db.get(`activity_${message.guild.id}_${message.author.id}`)
      message.reply({embeds:[
        new MessageEmbed().setDescription(`<:Message:1010885858792067192>  **${message.author.tag}** has sent ${data || 0} messages`).setColor(color)
      ]})
        } else{
                let data = db.get(`activity_${message.guild.id}_${mentionedMember.user.id}`)
      message.reply({embeds:[
        new MessageEmbed().setDescription(`<:Message:1010885858792067192>  **${mentionedMember.user.tag}** has sent ${data || 0} messages`).setColor(color)
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