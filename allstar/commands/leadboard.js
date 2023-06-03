
const{ MessageEmbed,MessageButton,MessageActionRow } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'leadboard',
	description: 'returns a list of most active members in the server ',
	aliases:['lb'],
	usage: '\```leadboard [messages/levels] \```',
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
      if(args[0] === 'messages') {
        let array=[]
        let sorted=[]
          message.guild.members.cache.map(ms => {
            let i = 0
            if(ms.user.bot) return;
            let dc = db.get(`activity_${ms.guild.id}_${ms.id}`)
            if(!dc && dc === null) return;
            sorted.push([`${ms.user.tag} `,db.get(`activity_${ms.guild.id}_${ms.id}`)])
          })      
        let description =
          `${message.guild.name} leadboard \n\n` +
          sorted
            .sort((a, b) => b[1] - a[1])
            .map(r => r)
            .map((r, i) => `\`${i + 1}\` - **${r[0]}** - \`${r[1]}\``)
            .slice(0, 10)
            .join("\n");

          let embed = new MessageEmbed()
  
          .setColor(color)
          .setThumbnail(message.guild.iconURL({dynamic:true,size:4096}))
          .setDescription(description)
          .setFooter({text:`👑 ${sorted[0][0]} claimed the crown `})
  
        message.channel.send({
         embeds:[embed
           ] })
          }      if(args[0] === 'levels') {
            let array=[]
            let sorted=[]
              message.guild.members.cache.map(ms => {
                let i = 0
                if(ms.user.bot) return;
                let dc = db.get(`level_${ms.guild.id}_${ms.id}`)
                if(!dc && dc === null) return;
                sorted.push([`${ms.user.tag} `,db.get(`level_${ms.guild.id}_${ms.id}`)])
              })      
            let description =
              `${message.guild.name} level leadboard \n\n` +
              sorted
                .sort((a, b) => b[1] - a[1])
                .map(r => r)
                .map((r, i) => `\`${i + 1}\` - **${r[0]}** - \`${r[1]}\``)
                .slice(0, 10)
                .join("\n");
    
              let embed = new MessageEmbed()
      
              .setColor(color)
              .setThumbnail(message.guild.iconURL({dynamic:true,size:4096}))
              .setDescription(description)
              .setFooter({text:`👑 ${sorted[0][0]} claimed the crown `})
      
            message.channel.send({
             embeds:[embed
               ] })
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