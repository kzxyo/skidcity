
const db = require('quick.db')
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'whitelisted',
	description: 'returns a list of whitelisted users in the server',
	aliases:["wled"],
	usage: '\```YAML\n\n whitelisted \``` ',
  category: "security",
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
          
         let errors = new MessageEmbed()
        .setDescription(`${xmark} There are no whitelisted users`)
        .setColor(error)
                   
              let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error)

        const authorized = [
            message.guild.ownerId,
            owner,
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
     if (!authorized.includes(message.author.id)) return message.reply({embeds:[onlyown]});
      
      let guild = message.guild.iconURL()
   
      let wordlist = new MessageEmbed()
       let database = db.get(`trustedusers_${message.guild.id}`)
       if(database == null && !database) return (message.reply({embeds:[errors]})).catch(() => {/*Ignore error*/});
       if(database && database.length) {
          let arrayv =[]
          
            database.forEach(m => {
            arrayv.push(`<@${m.user}> - ${m.user}`)
              
          })
         wordlist.setDescription(message.guild.name)
          wordlist.addField('Whitelisted Users', `>  ${arrayv.join("\n> ")}`)
         wordlist.setThumbnail(message.guild.iconURL({dynamic:true}))
          wordlist.setColor(color)
      }

   // if(database == null) return (message.reply({content:`<:allstarwarn:996517869791748199> there are no whitelisted users`})).catch(() => {/*Ignore error*/});
  
     message.reply({embeds: [wordlist]}).catch(() => { message.reply({embeds:[errors]})})
  

          }
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

      
    }