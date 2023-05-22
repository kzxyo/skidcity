
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'serverbanner',
	description: 'returns server banner',
	aliases:["sbanner","serverb"],
	usage: ' \```YAML\n\n sbanner \``` ',
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
                      const data = await axios.get(`https://discord.com/api/guilds/${message.guild.id}`, {
            headers:{
              Authorization:`Bot ${client.token}`
            }
          }).then(d => d.data);
          if(data.banner){
            let url = data.banner.startsWith("a_")?".gif?size=4096":".png?size=4096";
            url = `https://cdn.discordapp.com/banners/${message.guild.id}/${data.banner}${url}`
      
      const embed = new MessageEmbed()

        .setColor(color)
        .setTitle(`${message.guild.name}'s banner`)
        .setImage(url)
        message.reply({embeds:[embed]});
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