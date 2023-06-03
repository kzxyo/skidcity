
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'vanityjoins',
	description: 'returns vanity link and uses',
	aliases:[],
	usage: ' \```YAML\n\n vanityjoins \``` ',
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

      message.guild.fetchVanityData().then(async vanity => {
              let embed = new MessageEmbed()
      .setDescription(`<:MessageLink:1010885859735785553> https://discord.gg/${vanity.code} has ${vanity.uses} joins`)
     .setColor(color)
        //.setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})
        await message.reply({embeds:[embed]});
        
      }).catch(err => {message.reply({embeds:[{description:`${xmark} Your server doesn't have vanity`,color:error}]})})

      
      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};