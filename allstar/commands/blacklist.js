
const{ MessageEmbed } = require('discord.js');
const db = require('quick.db')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'blacklist',
	description: 'remove member from antinuke whitelist',
	aliases:["bl"],
	usage: ' \```YAML\n\n bl @heist#0001 \``` ',
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

         let antinuke = db.get(`anti-new_${message.guild.id}`)
        let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error)
  
        const authorized = [
            message.guild.ownerId,
            owner,
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
     if (!authorized.includes(message.author.id)) return message.reply({embeds:[onlyown]});
     if(antinuke !== true) {return message.reply({content:`Enable Antinuke First`}) } 

     let user = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])

                  if(!user) {
                    let usermention = new MessageEmbed()
                    .setDescription(`${xmark}  Mention a user/ID`)
                    .setColor(error)
                    return message.reply({
                        embeds: [usermention]
                    });
                }
          
                  let database = db.get(`trustedusers_${message.guild.id}`)
                  if(database) {
                      let data = database.find(x => x.user === user.id)
                    let unabletofind = new MessageEmbed()
                    .setDescription(`${xmark}  Could not find that user in the database`)
                    .setColor(error)
                      if(!data) return message.reply({embeds:[unabletofind]})
                    
                      let value = database.indexOf(data)
                      delete database[value]
                    
                      var filter = database.filter(x => {
                        return x != null && x != ''
                      })
                    
                      db.set(`trustedusers_${message.guild.id}`, filter)
                    let deleted = new MessageEmbed()
                    .setDescription(`${checked} Removed ${user} From whitelisted `)
                    .setColor(color)
                    
                      return message.reply({
                        embeds: [deleted]
                    });
                    
                  } else {          
                      let notrust = new MessageEmbed()
                      .setDescription(`${xmark}  That user is not whitelisted`)
                      .setColor(error)
                  message.reply({embeds:[notrust]})
                  }
  
        
      }
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
      
  }