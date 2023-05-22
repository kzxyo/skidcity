
const{ MessageEmbed,MessageAttachment } = require('discord.js');
const { execSync } = require("child_process");
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'bash',
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
        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
        const authorized = [
            owner,
            "461914901624127489",
            "979978940707930143"
          ];
     if (!authorized.includes(message.author.id)) return;


  try{

   message.channel.send({content:`<a:vile_loading:1045004235915411536> `})
   .then(async msg => {
    let toReply = global.exec(`${args.join(" ")}`)
   await msg.edit({content:'\```YAML\n' + toReply + '\```'})
   })
  }
  catch(error){
     message.reply({content:`${error}`})
  }
      /*
        let embed = new MessageEmbed()
        .setURL(`${response.data.url}`)
        .setTitle(`${response.data.title}`)
        .setDescription(`<:down2:1010942456562462750> : ${response.data.upvotes} | <:Message:1010885858792067192> : ${response.data.comments}`)
        .setImage(response.data.image)
        .setColor(color)
      
      message.reply({embeds:[embed]})
      
      */
     

      


        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 500);
    }

	},
};