
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'boostercount',
	description: 'returns booster count and premium tier',
	aliases:["boosters","boosts"],
	usage: ' \```YAML\n\n boosts \``` ',
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

      
      let embed = new MessageEmbed()
        .addField(`Booster Count `,`> <:allstarboost:997232872509427833>  Boosts ${message.guild.premiumSubscriptionCount} \n> <:allstarboostlvl2:997557580836638830> Level ${message.guild.premiumTier.replace('TIER_', '' && 'NONE','0')}`)
        .setColor("#f47fff")
        //.setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})
        await message.reply({embeds:[embed]});
      
      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};