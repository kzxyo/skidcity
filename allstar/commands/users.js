
const{ MessageEmbed } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'users',
	description: '',
	aliases:[],
	usage: '',
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
              const authorized = [
          "812126383077457921",
          "839221856976109608",
                "979978940707930143",
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return;

      let embed = new MessageEmbed()
      .setDescription(`${db.get(`privacy`).length} Users Accepted [Privacy Policy](https://nekokouri.gitbook.io/allstar/details/privacy-policy) \n ${db.get(`blacklisted`).length} Denied [Privacy Policy](https://nekokouri.gitbook.io/allstar/details/privacy-policy)`)
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