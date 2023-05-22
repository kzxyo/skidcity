
const db = require('quick.db')
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'whitelist',
	description: 'whitelist a trusted user so antinuke events dont get triggered ',
	aliases:["wl"],
	usage: '\```YAML\n\n whitelist @heist#0001 \``` ',
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

       if(antinuke !== true) return message.reply({embeds:[{description:`${xmark} You need to enable antinuke first.`,color:error}]}) 
        let user = message.mentions.users.first()  || message.guild.members.cache.get(args[0]);
        if(!user) {
            let usermention = new MessageEmbed()
            .setDescription(`
            ${xmark}  Mention user to whitelist
            `)
            .setColor(error)
    
            return message.reply({
                embeds: [usermention]
            });
        }
        let trustedusers = db.get(`trustedusers_${message.guild.id}`)
        if(trustedusers && trustedusers.find(find => find.user == user.id)) {
          let trust = new MessageEmbed()
          .setColor(error)
          .setDescription(`${xmark} That user is already whitelisted`)
        return message.reply({embeds:[trust]})
        }
let data = {
    user: user.id
}
        db.push(`trustedusers_${message.guild.id}`, data)
        let added = new MessageEmbed()
        .setDescription(`
       ${checked} ${user.username} has been whitelisted
        `)
        .setColor(color)

        return message.reply({
            embeds: [added]
        });
      }
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
    
  }