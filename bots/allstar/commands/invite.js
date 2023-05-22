
const{ MessageEmbed,MessageActionRow,MessageButton } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'invite',
	description: 'returns bot direct invite',
	aliases:[],
	usage: '\```YAML\n\n invite \``` ',
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
             const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('Invite Me!')
         .setEmoji(`<:MessageLink:1010885859735785553> `)
         .setURL("https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands")
         .setStyle('LINK'),
        )

          let embed = new MessageEmbed()
        .setURL(`https://discord.gg/heist`)
        .setTitle(`Allstar`)
        .setDescription(`<:sensowelcoming:1031693657809616967>  Allstar Security & Multipurpose \n> Guilds \`${client.guilds.cache.size}\` \n> Users \`${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)}\``)
        .setColor(color)
        message.reply({embeds:[embed],components:[row]});

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};