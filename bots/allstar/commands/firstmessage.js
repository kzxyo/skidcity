
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'firstmessage',
	description: 'returns first message link sent in that channel',
	aliases:["firstmsg"],
	usage: '\```YAML\n\n firstmessage \``` ',
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
      
          const fetchMessages = await message.channel.messages.fetch({
      after: 1,
      limit: 1,
    });
      
      
          const msg = fetchMessages.first();

 
          let embed = new MessageEmbed()
        .setDescription(` <:Message:1010885858792067192> [Jump to First Message](${msg.url}) in this Channel`)
        .setColor(color)
        message.reply({embeds:[embed]});

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};