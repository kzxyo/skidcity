
const{ MessageEmbed,Util,MessageActionRow,MessageButton } = require('discord.js');
const db = require('quick.db')
const parse = require('../regex.js')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'boost',
	description: 'replies to new boosters with custom message',
	aliases:['boostevent','booster'],
	usage: ' \``` boost channel {channel.id} \n boost message {msg} \n boost clear \n boost stats \``` ',
  category: "config",
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
      let emoji = `<:allstarreply:1032192256192553030> `
      if(!args[0]){
        let embed = new MessageEmbed()
        .setDescription(`**Booster Commands** \n <:allstarreply:1032192256192553030> boost message {message}\n <:allstarreply:1032192256192553030> boost channel {#channel} \n <:allstarreply:1032192256192553030> boost variables \n <:allstarreply:1032192256192553030> boost clear `)
        .setColor(color)
        return message.reply({embeds:[embed]})
        }
      if(args[0] === 'channel'){
     let channel = message.mentions.channels.first()
      if (!channel) return message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} Mention a valid channel`).setColor(error)]});
       message.reply({embeds:[new MessageEmbed().setDescription(`${checked} Set the boosters channel to <#${channel.id}>`).setColor(color)]});
       db.set(`boostchan_${message.guild.id}`, channel.id)
      }else if(args[0] === 'message'){
        message.reply({embeds:[new MessageEmbed().setDescription(`${checked} updated boosters message`).setColor(color)]});
        db.set(`boostmsg_${message.guild.id}`, args.splice(1).join(' '))
      }else if(args[0] === 'clear'){
        message.reply({embeds:[new MessageEmbed().setDescription(`${checked} Cleared boosters setup from database`).setColor(color)]});
        db.delete(`boostchan_${message.guild.id}`)
        db.delete(`boostmsg_${message.guild.id}`)
        
      }else if(args[0] === 'variables'){
        let embed = new MessageEmbed()
        .setDescription(`**Booster Variables** <:allstarboost:1032192230963814410>  \n <:allstarreply:1032192256192553030>  {user} - ${message.member} \n <:allstarreply:1032192256192553030> {user.name} - ${message.author.username} \n <:allstarreply:1032192256192553030> {user.tag} - ${message.author.tag} \n <:allstarreply:1032192256192553030> {user.id} - ${message.author.id} \n <:allstarreply:1032192256192553030> {boostcount} - ${message.guild.premiumSubscriptionCount} \n <:allstarreply:1032192256192553030> {levelcount} - ${message.guild.premiumTier.replace('TIER_', '' && 'NONE','0')} \n <:allstarreply:1032192256192553030> {guild.name} - ${message.member.guild.name} \n <:allstarreply:1032192256192553030> {guild.id} - ${message.member.guild.id}`)
        .setColor("#f47fff")
        message.reply({embeds:[embed]})
        }
      else if(args[0] == 'stats'){
             let chx = db.get(`boostchan_${message.guild.id}`);
      if (chx) chx = `<#${chx}>`
      else if (chx === null) chx = `Not Set`
            let welcome = db.get(`boostmsg_${message.guild.id}`)
      if (welcome === null)   welcome = 'Not Set'
              let stats = new MessageEmbed()
      .setDescription(`<a:allstarwelcome:996512695480238182> ${message.guild.name} Booster Stats `)
      .setColor("#f47fff")
            .addFields({
        name:`Boost Channel`,
        value: `${emoji} ${chx}`,
        inline: true,
    },
    {
        name:`Boost Message`,
        value:`${emoji} ${welcome}`,
        inline:true
    },


)
       message.reply({embeds:[stats]})
      }
      else if(args[0] == 'test'){
               let channel = db.get(`boostchan_${message.guild.id}`)
       let welcome = db.get(`boostmsg_${message.guild.id}`)
       
      welcome = welcome.replace('{user}', message.member);
      welcome = welcome.replace('{user.name}', message.author.username);
      welcome = welcome.replace('{user.tag}', message.author.tag);
      welcome = welcome.replace('{user.id}', message.author.id);
      welcome = welcome.replace('{boostcount}', message.guild.premiumSubscriptionCount);
      welcome = welcome.replace('{levelcount}', message.guild.premiumTier.replace('TIER_', '' && 'NONE','0'));
      welcome = welcome.replace('{guild.name}', message.member.guild.name);
      welcome = welcome.replace('{guild.id}', message.member.guild.id);
       if(channel && welcome) client.channels.cache.get(channel).send({embeds:[
       {
         description:welcome,
         color:color
       }
       ]})
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