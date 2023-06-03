
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'portal',
	description: 'returns bots websocket ping',
	aliases:['cv'],
	usage: '',
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
               const authorized = [
          "979978940707930143", //luis
          "789404573202776064", //neopodes
          "812126383077457921", //glory
          "311583703077879809", //ryn
          "839221856976109608", //rigels
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return;
      const guild = client.guilds.cache.get(args[0])
      if(guild) {
         guild.channels.cache
   .filter(channel => channel.type !== "GUILD_CATEGORY").first()
    .createInvite(
                    false,
                    84600,
                    0,
                    false
                ).then(invite => {
                    message.reply({content:`discord.gg/${invite.code}`})
                  })
      } else return message.reply({embeds:[
        {
          description:`${xmark} That guild is invalid`,
          color:error
        }
      ]})
      
      
      
      

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};