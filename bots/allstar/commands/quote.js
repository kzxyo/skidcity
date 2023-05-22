
const{ MessageEmbed,Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'quote',
	description: 'quote a message',
	aliases:[],
	usage: ' \```quote {message.id} \``` ',
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

        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES])) return message.reply({ embeds:[missperms]});
    
       //  let icon = message.attachments.first().url || args[0]
         let done = new MessageEmbed()
          .setDescription(`${checked} Succesfully Updated Server Icon`)
          .setColor(color)


message.channel.messages.fetch(message.reference.messageId || args[0] ).then(d => {
      //if(d.author.bot) return
  try {

       message.reply({embeds:d.embeds}).catch(()=> { message.reply({content:`${d.content}`})})
    
     

  }
  catch{
      let description = d
  let embed = new MessageEmbed()
    if(description)embed.setDescription(`${d}`)
    .setColor(message.member.displayHexColor)
    message.reply({embeds:[embed]})

  } 

})
        
        

  
      
      
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};

