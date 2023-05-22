
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const urban = require('relevant-urban')
const talkedRecently = new Set();
module.exports = {
	name: 'urban',
	description: 'search definition of a word',
	aliases:[],
	usage: '\``` urban [argument] \```',
  category: "information",
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
         const search = await urban(args.join(" "))
         let embed = new MessageEmbed()
         .setThumbnail('https://images.newrepublic.com/a0a10f8123e4aeb5617a37ffd2f7f1449d1b69e1.jpeg')
         .setDescription(`**${search.word}** \n  ${search.definition} \n\n${search.example} `)
         .setColor(color)
         message.reply({embeds:[embed]})

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};