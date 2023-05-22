
const{ MessageEmbed,MessageAttachment,MessageActionRow,MessageButton } = require('discord.js');

const canvacord = require("canvacord");
const { default_prefix ,color,error,owner ,xmark} = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'status',
	description: 'shows mentioned user current status',
	aliases:[],
	usage: '\```status {user}',
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
    const toTimestamp = (strDate) => {
  const dt = Date.parse(strDate);
  return dt / 1000;
}

let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])

if(!mentionedMember) mentionedMember = message.guild.members.cache.get(message.author.id)
            if(mentionedMember.presence == null) return message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} That user is offline`).setColor(error)]})
      
      
            if(mentionedMember.presence.activities[0] === 'undefined') return  message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} ${mentionedMember.user.username} doesn't have an activity `).setColor(error)]})
           if(!mentionedMember.presence.activities[0]) return  message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} ${mentionedMember.user.username} doesn't have an activity `).setColor(error)]})
           
  try {
    
  
            let style = 'R'
            let started = `<t:${Math.floor(mentionedMember.presence.activities[0].timestamps.start/1000)}` + (style ? `:${style}` : '') + '>'
        
            const embed = new MessageEmbed()
            .setDescription(`${mentionedMember.user.username} is ${mentionedMember.presence.activities[0].type.toLowerCase() } ${mentionedMember.presence.activities[0].name} since ${started}`)
                .addFields(
                {
                  name:`Type`,
                  value:`${mentionedMember.presence.activities[0].type.toLowerCase() }`,
                  inline:true
                },
                  {
                    name:`Name`,
                    value:`${mentionedMember.presence.activities[0].name.toLowerCase() }`
                  }
                )
            .setColor(color)

            message.reply({embeds:[embed]}) 
               
  }catch{
                const embed = new MessageEmbed()
            .setDescription(`${mentionedMember.user.username} is ${mentionedMember.presence.activities[0].type.toLowerCase() } ${mentionedMember.presence.activities[0].name} `)
                .addFields(
                {
                  name:`Type`,
                  value:`${mentionedMember.presence.activities[0].type.toLowerCase() }`,
                  inline:true
                },
                  {
                    name:`Name`,
                    value:`${mentionedMember.presence.activities[0].name.toLowerCase() }`
                  }
                )
            .setColor(color)

            message.reply({embeds:[embed]}) 
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