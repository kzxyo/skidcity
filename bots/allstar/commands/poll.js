
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'poll',
	description: 'create a poll',
	aliases:[],
	usage: ' \```YAML\n\n poll am i gay? \``` ',
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
          
    
            let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing \`MANAGE_MESSAGES\` permission`)
        .setColor(error)
       let imissperms = new MessageEmbed()
        .setDescription(`${xmark}  i don't have perms`)
        .setColor(error)
    if (!message.member.permissions.has("MANAGE_MESSAGES")) return message.reply({embds:[missperms]});
    if (!message.guild.me.permissions.has("MANAGE_MESSAGES")) return message.reply({embeds:[imissperms]});
      
      let x = new MessageEmbed()
      .setDescription(`${xmark} You need to provide a question`)
      .setColor(error)
      
      
      if(!args[0]) return message.reply({embeds:[x]})
      if(message.attachments.first()) {

         let msg = args.join(' ');
          let embed = new MessageEmbed()
        .setDescription(` ${msg}`)
        .setColor(color)
      .setImage(`${message.attachments.first().url}`)
          .setFooter({text:`Poll Created by ${message.author.tag}`})
        message.channel.send({embeds:[embed]}).then(messageReaction => {
    messageReaction.react(`👍`);
    messageReaction.react(`👎`);
  })
      } else {

        let msg = args.join(' ');
        let embed = new MessageEmbed()
      .setDescription(` ${msg}`)
      .setColor(color)
        .setFooter({text:`Poll Created by ${message.author.tag}`})
      message.channel.send({embeds:[embed]}).then(messageReaction => {
  messageReaction.react(`👍`);
  messageReaction.react(`👎`);
})




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