
const{ MessageEmbed,Permissions,Util } = require('discord.js');
const Discord = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'steal',
	description: 'create multiple emojis at once',
	aliases:["createemoji"],
	usage: '\```YAML\n\n steal {emojis} \```',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
        let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing perms`)
        .setColor(error)
        let imissperms = new MessageEmbed()
        .setDescription(`${xmark}  i don't have perms`)
        .setColor(error)


        if (talkedRecently.has(message.author.id)) {
          const getEmoji = Util.parseEmoji(args[0]);
                if (getEmoji.id) {
        const emojiExt = getEmoji.animated ? '.gif' : '.png';
        const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`;
        await message.guild.emojis
          .create(emojiURL, getEmoji.name)
        let x = new MessageEmbed()
      .setDescription(`${checked} Created Emote ${args[0]}`)
       .setColor(color)
       return message.reply({embeds:[x]})
      }

             message.react(`⌛`)
    } else {

        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES]))  return message.reply({ embeds:[missperms]});
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES])) return message.reply({ embeds:[imissperms]});
      
      
          if (!args[0]) {
      const emojiEmbed = new MessageEmbed()
        .setDescription(`addemote <<emote>> \n example createmote <:jj_pls:996539162796769431> `)
        .setColor(color)
      if (!args[0]) return message.reply({embeds:[emojiEmbed]})
    }
     if(args[51]) {
       let too = new MessageEmbed()
       .setDescription(`${xmark} You can't create more than 50 emojis`)
       .setColor(error)
       return message.reply({embeds:[too]})
     }
      let emojiss = new Array();
    for (const emojis of args) {
      const getEmoji = Util.parseEmoji(emojis);

      if (getEmoji.id) {
        const emojiExt = getEmoji.animated ? '.gif' : '.png';
        const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`;
        await message.guild.emojis
          .create(emojiURL, getEmoji.name)
          .then((emoji) => (
          emojiss.push(emoji)
        ))
      }
    }
        let help = new MessageEmbed()
        .setDescription(`${checked} Succesfully Created ${emojiss.length} emojis `)
        .setColor(color)
    await message.reply({embeds:[help]});
    


      
      
      
      
      
      
      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id),
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 900000);
    }


	},
};
