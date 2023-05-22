
const{ MessageEmbed,EmbedBuilder } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const parse = require('../regex.js')
const talkedRecently = new Set();
module.exports = {
	name: 'credits',
	description: 'Bot Owners & staff',
	aliases:[],
	usage: '\```credits\```',
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
         .setAuthor({name:`Allstar `})
         .addFields(
            {
                name:`**Owners**`,
                value:` <:allstarreply:1032192256192553030>  \`1\` <:allstarowner:1031696748084740099>  **${client.users.cache.get('812126383077457921').tag}** - Owner (\`${client.users.cache.get('812126383077457921').id}\`) \n <:allstarreply:1032192256192553030> \`2\` <:allstarowner:1031696748084740099> **${client.users.cache.get('839221856976109608').tag}** - Owner & Developer (\`${client.users.cache.get('839221856976109608').id}\`) \n <:allstarreply:1032192256192553030> \`3\` <:allstarowner:1031696748084740099> **${client.users.cache.get('311583703077879809').tag}** - Owner (\`${client.users.cache.get('311583703077879809').id}\`) \n <:allstarreply:1032192256192553030>  \`4\` <:allstarowner:1031696748084740099> **${client.users.cache.get('979978940707930143').tag}** - Owner & Developer (\`${client.users.cache.get('979978940707930143').id}\`) \n <:allstarreply:1032192256192553030> \`5\` <:allstarowner:1031696748084740099> **${client.users.cache.get('461914901624127489').tag}** - Owner (\`${client.users.cache.get('461914901624127489').id}\`) \n`
            }
         )
         .setThumbnail(client.user.displayAvatarURL({dynamic:true,size:4096}))
         .setColor(color)
         message.reply({embeds:[embed]})

      
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};