
const{ MessageEmbed,MessageAttachment } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const canvacord = require("canvacord");
const talkedRecently = new Set();
module.exports = {
	name: 'wasted',
	description: 'returns wasted image',
	aliases:[],
	usage: '\```wasted {user}\```',
  category: "image",
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

      let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])
 
      let avatar = mentionedMember.user.displayAvatarURL({ dynamic: false, format: 'png' ,size:4096});
      let image = await canvacord.Canvas.wasted(avatar);
      let attachment = new MessageAttachment(image, "wasted.png");
      message.reply({files:[attachment]})
      
      
      
      
      
      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};